from screeninfo import get_monitors

class Resolution():
    DAR        = float(16/10)
    scalar     = 0.85 # visual space scalar of app
    hscalar    = 0.9 # map height
    
    def get_primary_display(self):
        if len(get_monitors()) == 1:
            print("ONE MONITOR")
            primary_monitor = get_monitors()[0]
        else:
            for m in get_monitors():
                print(str(m))
                if m.is_primary:
                    primary_monitor = m
                    
        return primary_monitor
    
    ''' 
    returns a tuple of (width,height,left,top)
    '''
    def set_dimensions(self):
        m = self.get_primary_display()
        
        dim = []
        dim.append(m.width)
        dim.append(m.height)
        
        w = int(m.width*self.scalar)
        h = int(w*(1/self.DAR))       
        l = int((dim[0] - w)/2)
        t = int((dim[1] - h)/2)
        
        return (w,h,l,t)