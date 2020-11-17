_C=False
_B='new'
_A=None
from itertools import chain
from typing import Callable,List,Tuple,Union,Optional
from functools import reduce
class StateMan:
	__slots__=['bindings','global_bindings','dependencies','dependents','static_props','dynamic_props','refs','cache','nocache']
	def __init__(A,props,literal=_C,refs=_A):
		C=props;A.bindings={};A.global_bindings=[];A.dependents={};A.static_props={};A.dynamic_props={};A.cache={};A.nocache=[];A.refs=refs if refs is not _A else{}
		if literal:A.static_props=C;A.dependents={A:[]for(A,B)in C}
		else:
			for D in C:
				B=C[D]
				if StateMan._is_dynamic_prop_definition(B):A.track_dynamic(D,*B)
				else:A.track_static(D,B)
	def bind(B,prop_or_props,handler):
		C=handler;A=prop_or_props
		if isinstance(A,(list,tuple)):
			for D in A:B.bind(D,C)
		elif A in B.static_props or A in B.dynamic_props:
			if A not in B.bindings:B.bindings[A]=[C]
			else:B.bindings[A].append(C)
		else:B.__missing__(A)
	def bind_all(A,handler):A.global_bindings.append(handler)
	def track_static(A,prop,value):
		B=prop
		if B not in A.dependents:A.dependents[B]=[]
		A.static_props[B]=value
		for C in A.global_bindings:C(_B,A,B)
	def track_dynamic(A,prop,getter,dependencies,setter=_A,cache=True):
		B=prop
		if B not in A.dependents:A.dependents[B]=[]
		A.dynamic_props[B]=getter,setter
		for C in dependencies:
			if C not in A.dependents:A.dependents[C]=[B]
			else:A.dependents[C].append(B)
		if not cache:A.nocache.append(B)
		for D in A.global_bindings:D(_B,A,B)
	def __len__(A):return len(A.static_props)+len(A.dynamic_props)
	def __iter__(A):return chain(A.static_props,A.dynamic_props)
	def __reversed__(A):return chain(reversed(A.dynamic_props),reversed(A.static_props))
	def __missing__(A,item):raise KeyError(f"Property {item} not found")
	def __contains__(A,item):return item in A.static_props or item in A.dynamic_props
	def __getitem__(A,item):
		B=item
		if B in A.static_props:return A.static_props[B]
		elif B in A.dynamic_props:
			if B in A.nocache:return A.dynamic_props[B][0](A)
			else:
				if B not in A.cache:A.cache[B]=A.dynamic_props[B][0](A)
				return A.cache[B]
		else:A.__missing__(B)
	def _walk_deps(A,item):return reduce(lambda a,b:a+b,[A._walk_deps(B)for B in A.dependents[item]],[item])
	def _handle_change(A,item):
		D=list(dict.fromkeys(A._walk_deps(item)))
		for B in D:
			if B in A.dynamic_props and B not in A.nocache and B in A.cache:A.cache.pop(B)
		for B in D:
			for C in A.global_bindings:C('changed',A,B)
			if B in A.bindings:
				for C in A.bindings[B]:C(A,B)
	def __setitem__(A,item,value):
		C=value;B=item
		if B in A.dynamic_props:
			if A.dynamic_props[B][1]is not _A:A.dynamic_props[B][1](A,C)
			else:raise TypeError(f"No setter for dynamic property {B}")
		elif B in A.static_props:A.static_props[B]=C;A._handle_change(B)
		else:
			A.track_static(B,C)
			for D in A.global_bindings:D(_B,A,B)
	@staticmethod
	def _is_dynamic_prop_definition(definition):
		A=definition
		if isinstance(A,(list,tuple)):B=len(A);return(B==2 or B==3 and callable(A[2])and(not B==4 or isinstance(A[3],bool)))and callable(A[0])and isinstance(A[1],(list,tuple))
		else:return _C