# Inquiry-Web v1.0
# Signature: Yasin Yaşar

import socket
import concurrent.futures
from typing import Dict, Any, List
import dns.resolver

class DNSChecker:
    def __init__(self, timeout: int = 3):
        self.timeout = timeout
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
    
    def get_records(self, domain: str, record_type: str) -> List[str]:
        try:
            if record_type == 'A':
                return socket.gethostbyname_ex(domain)[2]
            
            answers = self.resolver.resolve(domain, record_type)
            
            if record_type == 'MX':
                return [(answer.preference, str(answer.exchange)) for answer in answers]
            elif record_type == 'TXT':
                return [str(answer).strip('"') for answer in answers]
            else:
                return [str(answer) for answer in answers]
                
        except Exception:
            return []

    def check_all(self, domain: str) -> Dict[str, Any]:
        record_types = ['A', 'CNAME', 'MX', 'TXT', 'NS']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_type = {
                executor.submit(self.get_records, domain, record_type): record_type
                for record_type in record_types
            }
            
            results = {'domain': domain}
            for future in concurrent.futures.as_completed(future_to_type):
                record_type = future_to_type[future]
                results[record_type] = future.result()
                
        return results

    def format_results(self, results: Dict[str, Any]) -> str:
        output = [f"Domain: {results['domain']}"]
        
        if results['A']:
            output.append(f"A Records:")
            output.extend(ip for ip in results['A'])
            
        if results['CNAME']:
            output.append(f"CNAME Records:")
            output.extend(cname for cname in results['CNAME'])
            
        if results['MX']:
            output.append(f"MX Records:")
            output.extend(f"{host} (priority: {pref})" 
                         for pref, host in sorted(results['MX']))
            
        if results['TXT']:
            output.append(f"TXT Records:")
            output.extend(txt for txt in results['TXT'])
            
        if results['NS']:
            output.append(f"NS Records:")
            output.extend(ns for ns in results['NS'])
            
        return '\n'.join(output)

def handle_dns_records(args):
    if args.dns_records:
        checker = DNSChecker()
        results = checker.check_all(args.url)
        print(checker.format_results(results))
