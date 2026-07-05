from sqlmodel import Session, select

from models import Hero, HeroCreate


def create_hero(session: Session, hero: HeroCreate) -> Hero:
    """创建新英雄。"""
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


def get_heroes(session: Session, skip: int = 0, limit: int = 10) -> list[Hero]:
    """分页查询英雄列表。"""
    statement = select(Hero).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_hero(session: Session, hero_id: int) -> Hero | None:
    """根据 ID 查询英雄。"""
    return session.get(Hero, hero_id)


def update_hero(session: Session, db_hero: Hero, hero_data: HeroCreate) -> Hero:
    """更新英雄信息。"""
    hero_dict = hero_data.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_dict)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


def delete_hero(session: Session, db_hero: Hero) -> None:
    """删除英雄。"""
    session.delete(db_hero)
    session.commit()
