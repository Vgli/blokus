class Event:
    """this is a superclass for any events that might be generated by an
    object and sent to the EventManager
    """
    def __init__(self):
        pass

class TickEvent(Event):
    def __init__(self):
        pass

class QuitEvent(Event):
    def __init__(self):
       pass

class StartGameEvent(Event):
    def __init__(self):
        pass

class PygameEvent(Event): #Holder class for pygame events
    def __init__(self, ev):
        self.ev = ev

class NextTurn(Event):
    def __init__(self):
        pass

class GetPiece(Event):
    def __init__(self, num):
        self.num = num

class RotPiece(Event):
    def __init__(self, rottype):
        self.rottype = rottype

class NextPiece(Event):
    def __init__(self, direction):
        self.direction = direction

class SwitchPiece(Event):
    def __init__(self, size, piece):
        self.s = size
        self.p = piece

class MovePiece(Event):
    def __init__(self, direction = None, pos = None):
        self.direction = direction
        self.pos = pos

class PlacePiece(Event):
    def __init__(self):
        pass

class ResignEvent(Event):
    def __init__(self):
        pass

class EventManager:
    """this object is responsible for coordinating most communication
    between the Model, View, and Controller.
    """
    def __init__(self ):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()

    #----------------------------------------------------------------------
    def RegisterListener( self, listener ):
        self.listeners[ listener ] = 1

    #----------------------------------------------------------------------
    def UnregisterListener( self, listener ):
        if listener in self.listeners.keys():
            del self.listeners[ listener ]
        
    #----------------------------------------------------------------------
    def Post( self, event ):
        """Post a new event.  It will be broadcast to all listeners"""
        for listener in self.listeners.keys():
            #NOTE: If the weakref has died, it will be 
            #automatically removed, so we don't have 
            #to worry about it.
            listener.Notify( event )
