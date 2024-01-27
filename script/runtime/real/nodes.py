from __future__ import annotations
from typing import Iterable

from .. import factory

class RealRuntimeFactory(factory.RuntimeFactory):
    def __init__(self, callable: bool, callable_unpack_single_output: bool):
        super().__init__()
        self._callable = callable
        self._callable_unpack_single_output = callable_unpack_single_output

    def new_node(self, info: dict, defaults: dict, output_types: list[type]):
        import nodes

        c = nodes.NODE_CLASS_MAPPINGS[info['name']]

        # Directly modify class or subclass?
        # Subclass will add another layer of abstraction, which is the opposite to the goal of real mode.
        if self._callable:
            if not hasattr(c, 'create'):
                def create(comfy_script_c=c, comfy_script_orginal_new=c.__new__):
                    obj = comfy_script_orginal_new(comfy_script_c)
                    obj.__init__()
                    return obj
                setattr(c, 'create', create)

            def new(cls, *args, comfy_script_orginal_new=c.__new__, **kwds):
                obj = comfy_script_orginal_new(cls)
                obj.__init__()

                # Call the node
                outputs = getattr(obj, obj.FUNCTION)(*args, **kwds)
                
                # See ComfyUI's `get_output_data()`
                if self._callable_unpack_single_output and isinstance(outputs, Iterable) and not isinstance(outputs, dict) and len(outputs) == 1:
                    return outputs[0]
                return outputs
            c.__new__ = new
        
        return c

def load(nodes_info: dict, vars: dict | None, callable: bool = True, callable_unpack_single_output: bool = True) -> None:
    '''
    - `callable`: Make the nodes callable. Such that
      
      ```
      obj = MyNode()
      getattr(obj, MyNode.FUNCTION)(args)
      ```
      can be written as `MyNode(args)`.

      You can still create the node object by `MyNode.create()`.
    
    - `callable_unpack_single_output`: Unpack the returned tuple if it has only one item.
      
      In ComfyUI, the return value of a node is a tuple even there is only one output. For example, `EmptyLatentImage()` will return `(Latent,)` instead of `Latent`. So that
      ```python
      latent = EmptyLatentImage()
      ```
      have to be replaced with
      ```python
      latent, = EmptyLatentImage()
      ```
      without `callable_unpack_single_output`.
    '''
    fact = RealRuntimeFactory(callable, callable_unpack_single_output)
    for node_info in nodes_info.values():
        fact.add_node(node_info)
    
    globals().update(fact.vars())
    __all__.extend(fact.vars().keys())

    # if vars is None:
    #     # TODO: Or __builtins__?
    #     vars = inspect.currentframe().f_back.f_globals
    if vars is not None:
        vars.update(fact.vars())

    # nodes.pyi
    with open(__file__ + 'i', 'w', encoding='utf8') as f:
        f.write(fact.type_stubs())

__all__ = []