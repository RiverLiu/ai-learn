from fastapi import FastAPI, HTTPException

from crud import (
    create_hero,
    delete_hero,
    get_hero,
    get_heroes,
    update_hero,
)
from database import SessionDep, create_db_and_tables, engine
from models import HeroCreate, HeroPublic

app = FastAPI()


@app.on_event("startup")
def on_startup():
    """应用启动时创建数据库表。"""
    create_db_and_tables()


@app.post("/heroes/", response_model=HeroPublic, status_code=201)
def create_hero_endpoint(hero: HeroCreate, session: SessionDep):
    """创建英雄。"""
    return create_hero(session, hero)


@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(session: SessionDep, skip: int = 0, limit: int = 10):
    """查询英雄列表。"""
    return get_heroes(session, skip=skip, limit=limit)


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    """根据 ID 查询英雄。"""
    db_hero = get_hero(session, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="英雄不存在")
    return db_hero


@app.put("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero_endpoint(hero_id: int, hero: HeroCreate, session: SessionDep):
    """更新英雄。"""
    db_hero = get_hero(session, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="英雄不存在")
    return update_hero(session, db_hero, hero)


@app.delete("/heroes/{hero_id}")
def delete_hero_endpoint(hero_id: int, session: SessionDep):
    """删除英雄。"""
    db_hero = get_hero(session, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="英雄不存在")
    delete_hero(session, db_hero)
    return {"ok": True}
