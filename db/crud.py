from sqlalchemy import select, update
from db.base import AsyncSessionLocal
from db.models import User
from utils.calculations import calculate_macros

async def get_user_by_telegram(telegram_id: int):
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return q.scalars().first()

async def create_or_update_user_from_dict(telegram_id: int, data: dict):
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.telegram_id==telegram_id))).scalars().first()
        if not user:
            user = User(telegram_id=telegram_id, **data)
            session.add(user)
        else:
            for k, v in data.items():
                setattr(user, k, v)
        # recalc macros if enough fields
        if user.weight and user.height and user.age and user.gender and user.activity and user.goal:
            macros = calculate_macros(user.weight, user.height, user.age, user.gender, user.activity, user.goal)
            user.calorie_goal = macros["calories"]
            user.protein_goal = macros["protein"]
            user.fat_goal = macros["fat"]
            user.carb_goal = macros["carbs"]
        await session.commit()
        await session.refresh(user)
        return user

async def set_user_profile(telegram_id: int, **kwargs):
    return await create_or_update_user_from_dict(telegram_id, kwargs)
