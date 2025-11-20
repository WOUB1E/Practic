import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# --- Копируем модель Product из вашего приложения ---
# В реальном проекте лучше вынести модели в models.py и импортировать их
Base = declarative_base()


# --- Настройка подключения к базе данных ---
# ЗАМЕНИТЕ на ваши данные
DATABASE_URI = 'postgresql://postgres:1@localhost:5432/postgres'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Создаем таблицу, если ее еще нет
Base.metadata.create_all(engine)


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True) # article
    name = Column(String(255), nullable=False)
    unit = Column(String(255), nullable=False)
    cost = Column(Integer, nullable=False)
    provider = Column(String(255), nullable=False)
    maker = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    sale = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    disc = Column(String(255), nullable=False)
# --- Логика импорта ---

# Путь к вашему Excel файлу
file_path = r'data/products.xlsx'

try:
    # Читаем Excel файл
    df = pd.read_excel(file_path)
    
    print(f"Найдено {len(df)} записей в файле {file_path}. Начинаю импорт...")

    for index, row in df.iterrows():
        # Проверяем, существует ли товар с таким же артикулом (id)
        product_id = int(row['Артикул'])
        existing_product = session.query(Product).filter_by(id=product_id).first()
        
        if existing_product:
            print(f"Пропуск товара с артикулом '{product_id}': уже существует.")
            continue

        # Создаем новый товар, конвертируя данные в нужные типы
        try:
            new_product = Product(
                id=product_id,
                name=str(row['Наименование']),
                unit=str(row['Ед.измерения']),
                cost=int(row['Цена']),
                provider=str(row['Поставщик']),
                maker=str(row['Производитель']),
                category=str(row['Категория']),
                sale=int(row['Действующая скидка']),
                cost_with_sale = float(int(row['Цена'])*(1-int(row['Действующая скидка'])/100)),
                count=int(row['Количество на складе']),
                disc=str(row['Описание товара'])
            )
            session.add(new_product)
            print(f"Товар '{new_product.name}' (арт. {new_product.id}) добавлен в сессию.")
        except (ValueError, KeyError) as e:
            print(f"Ошибка в строке {index + 2}: {e}. Пропуск.")
            continue


    # Сохраняем все изменения в базе данных
    session.commit()
    print("\nИмпорт успешно завершен!")

except FileNotFoundError:
    print(f"Ошибка: Файл '{file_path}' не найден. Убедитесь, что он находится в той же папке.")
except Exception as e:
    # В случае ошибки откатываем изменения
    session.rollback()
    print(f"\nПроизошла ошибка: {e}")
    print("Все изменения отменены.")

finally:
    # Закрываем сессию
    session.close()
