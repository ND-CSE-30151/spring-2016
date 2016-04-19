from tock import *

def transitions(m):
    """Convert from Tock's internal format to tuples (q, a, r, b, d), where
    - q is the current state
    - a is the symbol read
    - r is the new state
    - b is the symbol written
    - d (-1 or 1) is the direction moved
    """
    tuples = []
    for t in m.get_transitions():
        (q,), (a,) = t.lhs
        (r,), bstore = t.rhs
        tuples.append((q, a, r, bstore[0], bstore.position))
    return tuples

def tape_alphabet(m):
    """Return the tape alphabet (Gamma) of m."""
    gamma = {syntax.BLANK}
    for _, a, _, b, _ in transitions(m):
        gamma.add(a)
        gamma.add(b)
    return gamma

class Formula(object):
    """Stub class for representing Boolean formulas."""
    def __init__(self, s, t=None):
        self.s = s
        self.t = t
    def __and__(self, other):
        if other == False: return False
        if other == True: return self
        ss = "({})".format(self.s) if self.t == "|" else self.s
        os = "({})".format(other.s) if other.t == "|" else other.s
        return Formula(ss + " & " + os, "&")
    def __rand__(self, other):
        if other == False: return False
        if other == True: return self
    def __or__(self, other):
        if other == False: return self
        if other == True: return True
        return Formula(self.s + " | " + other.s, "|")
    def __ror__(self, other):
        if other == False: return self
        if other == True: return True
    def __invert__(self):
        if self.t in ["&", "|"]:
            return Formula("~({})".format(self.s), "~")
        else:
            return Formula("~" + self.s, "~")
    def __str__(self):
        return self.s

def make_phi(m, w, k):
    """Convert the run of NTM m on input w to a Boolean formula 
    that is satisfiable iff m accepts w in at most |w|**k steps."""
    n = len(w)
    nk = max(n**k, n+3)
    gamma = tape_alphabet(m)
    C = gamma | m.states | {"#"}
    q0 = m.get_start_state()
    [qf] = m.get_accept_states()
    x = {}
    for i in range(1,nk+1):
        for j in range(1,nk+1):
            for s in C:
                x[i,j,s] = Formula("x[{},{},{}]".format(i,j,s))

    phi_cell = True

    # For each cell,
    for i in range(1,nk+1):
        for j in range(1,nk+1):
            
            # the cell must have a value
            at_least_one = False
            for s in C:
                at_least_one |= x[i,j,s]

            # and the cell must have at most one value
            at_most_one = True
            for s in C:
                for t in C:
                    if s != t:
                        at_most_one &= ~x[i,j,s] | ~x[i,j,t]

            phi_cell &= at_least_one & at_most_one

    # The first row should be the initial configuration
    phi_start = True
    phi_start &= x[1,1,"#"]                 # endmarker
    phi_start &= x[1,2,m.get_start_state()] # head
    for i in range(n):
        phi_start &= x[1,i+3,w[i]]          # input symbols
    for i in range(n+3,nk):
        phi_start &= x[1,i,syntax.BLANK]    # blank symbols
    phi_start &= x[1,nk,"#"]                # endmarker

    # Each row should be a legal successor configuration of the row above it
    phi_move = True

    # For each 2x3 window,
    for i in range(1,nk):
        for j in range(1,nk-1):

            phi_legal = False

            for t1 in gamma | {"#"}:
                for t2 in gamma:
                    for t3 in gamma | {"#"}:
                        phi_legal |= (x[i,j,  t1] & x[i,j+1,  t2] & x[i,j+2,  t3] &
                                      x[i+1,j,t1] & x[i+1,j+1,t2] & x[i+1,j+2,t3])

            for q, b, r, c, d in transitions(m):
                if d == -1: # move left: uaqbv becomes uracv
                    for u1 in gamma | {"#"}:
                        for u2 in gamma:
                            for a in gamma:
                                phi_legal |= (x[i,j,  u1] & x[i,j+1,  u2] & x[i,j+2,  a] &
                                              x[i+1,j,u1] & x[i+1,j+1,u2] & x[i+1,j+2,r])

                    for u2 in gamma | {"#"}:
                        for a in gamma:
                            phi_legal |= (x[i,j,  u2] & x[i,j+1,  a] & x[i,j+2,  q] &
                                          x[i+1,j,u2] & x[i+1,j+1,r] & x[i+1,j+2,a])

                    for a in gamma:
                        phi_legal |= (x[i,j,  a] & x[i,j+1,  q] & x[i,j+2,  b] &
                                      x[i+1,j,r] & x[i+1,j+1,a] & x[i+1,j+2,c])
                    # special case: if head is at left end, it does not move
                    phi_legal |= (x[i,j,  "#"] & x[i,j+1,  q] & x[i,j+2,  b] &
                                  x[i+1,j,"#"] & x[i+1,j+1,r] & x[i+1,j+2,c])

                    for a in gamma:
                        for v1 in gamma | {"#"}:
                            phi_legal |= (x[i,j,  q] & x[i,j+1,  b] & x[i,j+2,  v1] &
                                          x[i+1,j,r] & x[i+1,j+1,a] & x[i+1,j+2,v1])

                    for a in gamma:
                        for v1 in gamma:
                            for v2 in gamma | {"#"}:
                                phi_legal |= (x[i,j,  b] & x[i,j+1,  v1] & x[i,j+2,  v2] &
                                              x[i+1,j,a] & x[i+1,j+1,v1] & x[i+1,j+2,v2])

                elif d == +1: # move right: uaqbv becomes uacrv
                    for a in gamma:
                        for u in gamma | {"#"}:
                            phi_legal |= (x[i,j,  u] & x[i,j+1,  q] & x[i,j+2,  q] &
                                          x[i+1,j,u] & x[i+1,j+1,a] & x[i+1,j+2,c])

                    for a in gamma | {"#"}:
                        phi_legal |= (x[i,j,  a] & x[i,j+1,  q] & x[i,j+2,  b] &
                                      x[i+1,j,a] & x[i+1,j+1,c] & x[i+1,j+2,r])

                    for v1 in gamma:
                        phi_legal |= (x[i,j,  q] & x[i,j+1,  b] & x[i,j+2,  v1] &
                                      x[i+1,j,c] & x[i+1,j+1,r] & x[i+1,j+2,v1])

                    for v1 in gamma:
                        for v2 in gamma | {"#"}:
                            phi_legal |= (x[i,j,  b] & x[i,j+1,  v1] & x[i,j+2,  v2] &
                                          x[i+1,j,r] & x[i+1,j+1,v1] & x[i+1,j+2,v2])

                else:
                    raise ValueError("invalid direction")
            
            phi_move &= phi_legal

    # The accept state should occur somewhere
    phi_accept = False
    for i in range(1,nk+1):
        for j in range(1,nk+1):
            phi_accept |= x[i,j,qf]

    return phi_cell & phi_start & phi_move & phi_accept
