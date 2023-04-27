from dns import resolver
from dns.resolver import LifetimeTimeout

# DNS Adapter to get IP address in specified timeout/lifetime request
class MakeDNSRequest():
    
    def __init__(self, domain, timeout, lifetime, **kwargs):
        self.resolver = resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = lifetime
        self.domain = domain
        
    def DNSRequest(self):
        try: 
            query = self.resolver.resolve(self.domain, 'A')
            return query[0].to_text()
        except LifetimeTimeout:
            return False