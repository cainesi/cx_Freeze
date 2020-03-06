

class CopyTrace:
    def __init__(self, reason: str, predecessor: "CopyTrace"=None ):
        self.reason = reason
        self.predecessor = predecessor
        return

    def __str__(self) -> str:
        return self.reason

    def reportString(self, level: int) -> str:
        n = 0
        l = []
        trace = self
        while n < level:
            n += 1
            l.append("[{}] {}".format(n, str(trace)))
            trace = trace.predecessor
            if trace is None: break
            pass
        return " / ".join(l)