from typing import List, Dict
from parser import Statement, Expression, Definition, Type


class Member:
    def __init__(self, offs: int, ty: 'TypeLayout'):
        self.offs = offs
        self.ty = ty


class TypeLayout:
    INTEGRAL = "integral"

    storage = None

    name = None
    size = None
    align = None
    unsigned = None
    members = None

    @staticmethod
    def integral(name: str, size: int, align: int, unsigned: bool):
        tl = TypeLayout()
        tl.storage = TypeLayout.INTEGRAL
        tl.name = name
        tl.size = size
        tl.align = align
        tl.unsigned = unsigned
        return tl
    
    @staticmethod
    def struct(name: str, members: List[str, TypeLayout]):
        tl = TypeLayout()

        curr_offs = 0
        curr_align = 0

        member_dict = {}
        for mname, mlayout in members:
            curr_offs = (curr_offs + mlayout.align - 1) // mlayout.align * mlayout.align
            
            assert mname not in member_dict
            member_dict[mname] = Member(curr_offs, mlayout)
            
            curr_offs += mlayout.size
            curr_align = max(curr_align, mlayout.align)
        
        tl.size = curr_offs
        tl.align = curr_align
        tl.members = member_dict
        return tl
    
    @staticmethod
    def union(name: str, members: List[str, TypeLayout]):
        tl = TypeLayout()

        curr_size = 0
        curr_align = 0

        member_dict = {}
        for mname, mlayout in members:
            assert mname not in member_dict
            member_dict[mname] = Member(0, mlayout)
            
            curr_size = max(curr_size, mlayout.size)
            curr_align = max(curr_align, mlayout.align)
        
        tl.size = curr_size
        tl.align = curr_align
        tl.members = member_dict
        return tl




def typelist(defs: List[Definition]):
    defined_types: Dict[str, TypeLayout] = {
        "signed char":          TypeLayout.integral("signed char",          size=1, align=1, unsigned=False),
        "char":                 TypeLayout.integral("char",                 size=1, align=1, unsigned=True),
        "unsigned char":        TypeLayout.integral("unsigned char",        size=1, align=1, unsigned=True),
        "short":                TypeLayout.integral("short",                size=2, align=2, unsigned=False),
        "unsigned short":       TypeLayout.integral("unsigned short",       size=2, align=2, unsigned=True),
        "int":                  TypeLayout.integral("int",                  size=4, align=4, unsigned=False),
        "unsigned":             TypeLayout.integral("unsigned",             size=4, align=4, unsigned=True),
        "long":                 TypeLayout.integral("long",                 size=4, align=4, unsigned=False),
        "unsigned long":        TypeLayout.integral("unsigned long",        size=4, align=4, unsigned=True),
        "long long":            TypeLayout.integral("long long",            size=8, align=8, unsigned=False),
        "unsigned long long":   TypeLayout.integral("unsigned long long",   size=8, align=8, unsigned=True),
    }

