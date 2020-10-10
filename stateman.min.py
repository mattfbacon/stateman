M=False
L=callable
K=reversed
J=print
I='new'
H=len
G=tuple
E=None
D=list
C=isinstance
from itertools import chain as A
from typing import Callable,List,Tuple,Union,Optional
from functools import reduce as B
class F:
	__slots__=['bindings','global_bindings','dependencies','dependents','static_props','dynamic_props','refs','cache','nocache']
	def __init__(A,props,literal=M,refs=E):
		C=props;A.bindings={};A.global_bindings=[];A.dependents={};A.static_props={};A.dynamic_props={};A.cache={};A.nocache=[];A.refs=refs if refs is not E else{}
		if literal:A.static_props=C;A.dependents={A:[]for(A,B)in C}
		else:
			for D in C:
				B=C[D];J(B,F._is_dynamic_prop_definition(B))
				if F._is_dynamic_prop_definition(B):A.track_dynamic(D,*B)
				else:A.track_static(D,B)
	def bind(B,prop_or_props,handler):
		E=handler;A=prop_or_props
		if C(A,(D,G)):
			for F in A:B.bind(F,E)
		elif A in B.static_props or A in B.dynamic_props:
			if A not in B.bindings:B.bindings[A]=[E]
			else:B.bindings[A].append(E)
		else:B.__missing__(A)
	def bind_all(A,handler):A.global_bindings.append(handler)
	def track_static(A,prop,value):
		B=prop
		if B not in A.dependents:A.dependents[B]=[]
		A.static_props[B]=value
		for C in A.global_bindings:C(I,A,B)
	def track_dynamic(A,prop,getter,dependencies,setter=E,cache=True):
		B=prop
		if B not in A.dependents:A.dependents[B]=[]
		A.dynamic_props[B]=getter,setter
		for C in dependencies:
			if C not in A.dependents:A.dependents[C]=[B]
			else:A.dependents[C].append(B)
		if not cache:A.nocache.append(B)
		for D in A.global_bindings:D(I,A,B)
	def __len__(A):return H(A.static_props)+H(A.dynamic_props)
	def __iter__(B):return A(B.static_props,B.dynamic_props)
	def __reversed__(B):return A(K(B.dynamic_props),K(B.static_props))
	def __missing__(A,item):raise KeyError(f"Property {item} not found")
	def __contains__(A,item):return item in A.static_props or item in A.dynamic_props
	def __getitem__(A,item):
		B=item
		if B in A.static_props:return A.static_props[B]
		elif B in A.dynamic_props:
			if B in A.nocache:J('nocache for prop');return A.dynamic_props[B][0](A)
			else:
				if B not in A.cache:A.cache[B]=A.dynamic_props[B][0](A)
				return A.cache[B]
		else:A.__missing__(B)
	def _walk_deps(A,item):return B(lambda a,b:a+b,[A._walk_deps(B)for B in A.dependents[item]],initial=[item])
	def _handle_change(A,item):
		E=D(dict.fromkeys(A._walk_deps(item)))
		for B in E:
			if B in A.dynamic_props and B not in A.nocache and B in A.cache:A.cache.pop(B)
		for B in E:
			for C in A.global_bindings:C('changed',A,B)
			if B in A.bindings:
				for C in A.bindings[item]:C(A,B)
	def __setitem__(A,item,value):
		C=value;B=item
		if B in A.dynamic_props:
			if A.dynamic_props[B][1]is not E:A.dynamic_props[B][1](A,C)
			else:raise TypeError(f"No setter for dynamic property {B}")
		elif B in A.static_props:A.static_props[B]=C;A._handle_change(B)
		else:
			A.track_static(B,C)
			for D in A.global_bindings:D(I,A,B)
	@staticmethod
	def _is_dynamic_prop_definition(definition):
		A=definition
		if C(A,(D,G)):B=H(A);return(B==2 or B==3 and L(A[2])and(not B==4 or C(A[3],bool)))and L(A[0])and C(A[1],(D,G))
		else:return M