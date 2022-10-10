from scapy.all import TCP, rdpcap
import collections
import os
import re
import sys
import zlib

OUTDIR = '/root/Desktop/pictures'
PCAP = '/root/Desktop/training'

# 使用namedtuple可以通过属性名访问字段, 比字典消耗内存少, 提高可读性
Response = collections.namedtuple('Response', ['header', 'payload'])

def get_header(payload):
    # 读取原始HTTP流量
    try:
        # 提取HTTP头: 找到两个连续的\r\n
        header_raw = payload[:payload.index(b'\r\n\r\n')+2]
    except ValueError:
        # 若不存在两个连续的\r\n, 输出-后返回
        sys.stdout('-')
        sys.stdout.flush()
        return None
    # 将HTTP头里的每一行以冒号分割, 冒号左边是字段名, 冒号右边是字段值, 存进header字典
    header = dict(re.findall(r'(?P<name>.*?):(?P<value>.*?)\r\n', header_raw.decode()))
    if 'Content-Type' not in header:
        return None
    return header


def extract_content(Response, content_name='image'):
    # 接收一段HTTP响应数据
    content, content_type = None, None
    # 包含图片的响应头content-type里面都有image字样, 比如/image/png或/image/jpg
    if content_name in Response.header['Content-Type']:
        # 存储图片实际数据类型
        content_type = Response.header['Content-Type'].split('/')[1]
        content = Response.payload[Response.payload.index(b'\r\n\r\n')+4:]

        # 检查响应数据是否被压缩过
        if 'Content-Encoding' in Response.header:
            if Response.header['Content-Encoding'] == 'gzip':
                content = zlib.decompress(Response.payload, zlib.MAX_WBITS | 32)
            elif Response.header['Content-Encoding'] == 'deflate':
                content = zlib.decompress(Response.payload)
    return content, content_type


class Recapper:
    def __init__(self, fname):
        # 传入要读取的pcap文件路径
        pcap = rdpcap(fname)
        # 自动切分每个TCP会话, 并保存到一个字典里(每个会话都是一段完整的TCP数据流)
        self.sessions = pcap.sessions()
        self.responses = list()

    def get_responses(self):
        for session in self.sessions:
            payload = b''
            # 遍历每一个会话里的每一个数据包
            for packet in self.sessions[session]:
                try:
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                        # 类似于wireshark中右键单击一个数据包, 选择"follow TCP Stream"
                        payload += bytes(packet[TCP].payload)
                except IndexError:
                    # 有可能数据包中没有TCP数据
                    sys.stdout.write('x')
                    sys.stdout.flush()
            if payload:
                header = get_header(payload)
                if header is None:
                    continue
                self.responses.append(Response(header=header, payload=payload))

    def write(self, content_name):
        for i, response in enumerate(self.responses):
            content, content_type = extract_content(response, content_name)
            if content and content_type:
                # 命名为ex_i.[type], 例如ex_2.jpg
                fname = os.path.join(OUTDIR, f'ex_{i}.{content_type}')
                print(f'Writing {fname}')
                with open(fname, 'wb')as f:
                    f.write(content)


if __name__ == '__main__':
    pfile = os.path.join(PCAP, 'pcap.pcap')
    recapper = Recapper(pfile)
    recapper.get_responses()
    recapper.write('image')