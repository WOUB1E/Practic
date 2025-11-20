import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from enum import Enum

class Role(Enum):
    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

from sqlalchemy import Column, Integer, String, Enum as SQLEnum

DATABASE_URI = 'postgresql://postgres:1@localhost:5432/postgres'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
Base.metadata.create_all(engine) 

class User(Base): 
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(SQLEnum(Role), nullable=False)

role_mapping = {
    'Администратор': Role.ADMIN,
    'Менеджер': Role.MANAGER,
    'АвторизованныйКлиент': Role.USER
}

file_path = r'data\users.xlsx'

try:
    df = pd.read_excel(file_path)
    print(f"Найдено {len(df)} записей в файле {file_path}. Начинаю импорт...")

    for index, row in df.iterrows():
        
        login = row['Логин']
        password = row['Пароль']
        role_russian = row['Роль']

        
        existing_user = session.query(User).filter_by(username=login).first()
        if existing_user:
            print(f"Пропуск пользователя '{login}': уже существует.")
            continue

        
        role_enum = role_mapping.get(role_russian)
        if not role_enum:
            print(f"Пропуск строки {index + 2}: неизвестная роль '{role_russian}'")
            continue

        
        hashed_password = password
        new_user = User(
            username=login,
            password=hashed_password,
            role=role_enum
        )

        session.add(new_user)
        print(f"Пользователь '{login}' с ролью '{role_enum.value}' добавлен в сессию.")

    
    session.commit()
    print("\nИмпорт успешно завершен!")

except Exception as e:
    session.rollback()
    print(f"\nПроизошла ошибка: {e}")
    print("Все изменения отменены.")

finally:
    session.close()
