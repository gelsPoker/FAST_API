from typing import List, Optional, Dict

from itertools import count



from fastapi import FastAPI, HTTPException, Query

from pydantic import BaseModel, Field



app = FastAPI(title="FastAPI 8156", version="1.0.0")



class Item(BaseModel): 

    nombre: str = Field(min_length=1, description="Nombre Producto")

    precio: float = Field(gt=0, descripcion="Precio > 0")

    tags: List[str] = Field(default_factory=list)

    activo: bool = True



class ItemOut(Item):

    id: int



#Simular la base de datos

_db: Dict[int, Item] = {}

_id_seq = count(start=1)



# EndPoints

@app.get("/health", tags=["sistema"])

def health():

    return {"status":"ok"}



@app.get("/items", response_model=List[ItemOut])

def listar_items(

    q: Optional[str] = Query(None, description="Filtro por nombre que contenga 'q'"),

    skip: int = Query(0, ge=0),

    limit: int = Query(50, ge=1, le=200),

): 

    items = [

        ItemOut(id=i, **item.model_dump())

        for i, item in _db.items()

        if q is None or q.lower() in item.nombre.lower()

    ]

    return items[skip: skip + limit]



@app.post("/items", response_model=ItemOut, status_code=201, tags=["items"])

def crear_item(item: Item):

    new_id = next(_id_seq)

    _db[new_id] = item

    return ItemOut(id=new_id, **item.model_dump())



@app.get("/items/{item_id}", response_model=ItemOut, status_code=201)

def obtener_item(item_id: int):

    if item_id not in _db:

        raise HTTPException(status_code=404, detail="Item no encontrado")

    return ItemOut(id=item_id, **_db[item_id].model_dump())



@app.put("/items/{item_id}", response_model=ItemOut)

def actualizar_item(item_id: int, item: Item):

    if item_id not in _db:

        raise HTTPException(status_code=404, detail="Item no encontrado")

    _db[item_id] = item

    return ItemOut(id=item_id, **item.model_dump())



@app.delete("/items/{item_id}", status_code=204, tags=["items"])

def eliminar_item(item_id: int):

    if item_id not in _db:

        raise HTTPException(status_code=404, detail="Item no encontrado")

    del _db[item_id]

    return None