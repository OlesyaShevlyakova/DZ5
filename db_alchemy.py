from sqlalchemy import create_engine, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from utils import hash_password

"""
Реализация обращения к БД через SQL Alchemy.
Сложность с которой столкнулась - пришлось сначала делать описание по модели SQL Alchemy 1.4 вида:
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child")
Так как не смогла сходу понять что за модель декларативная модель ORM у версии 2.0
После этого, по документации "SQLAlchemy 2.0 - Major Migration Guide"
https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
Выполнила миграпцию описания к модели версии 2.0 представленной в коде ниже
"""


# Создаем базовый класс наследующийся от класса описания объеквто декларативным подходом
class Base(DeclarativeBase):
    pass


class UsersTable(Base):
    """
    Наследуем от базового декларативного класса
    Создаем таблицу хранения информации о пользователях
    Пароль хранится в хешированном виде
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(unique=True)

    def __repr__(self) -> dict:
        return "{'id': self.id,'name': self.name,'password': self.password}"


class AssetsTable(Base):
    """
    Наследуем от базового декларативного класса
    Создаем таблицу хранения информации об активах
    """
    __tablename__ = 'assets'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"))

    def __repr__(self) -> str:
        result = str({'id': self.id, 'name': self.name, 'amount': self.amount, 'date': self.date})
        return result


def init_db_alch():
    """
    Первичная инициализация БД
    """
    current_engine = get_db_alch()  # отекрываем подключение к БД
    Base.metadata.create_all(current_engine)  # создаем объекты, если они в БД остутствуют


def get_db_alch():
    """
    Функция установуки подключения к нашей БД
    """
    current_engine = create_engine('sqlite:///database.db', echo=True)
    return current_engine


def reg_user(login: str, password: str) -> tuple[bool, str]:
    """
    Регистрация пользователя
    На вход принимаем логин и пароль
    Возвращаем обратно тюпл из False - если есть ошибка или True если её не было
    и строки с текстом ошибки
    """
    current_engine = get_db_alch()
    with (Session(current_engine) as session):
        # сначала проверим, что логин свободен
        stmt = select(UsersTable).where(UsersTable.name == login)
        result = session.execute(stmt)
        result = result.all()
        if len(result) != 0:  # значит что-то нашли
            return False, 'Такой логин уже присутствует'
        else:  # иначе значит логин свободен
            new_user = UsersTable(
                name=login,
                password=hash_password(password)
            )
            session.add_all([new_user])
            session.commit()
            return True, 'Пользователь успешно добавлен, авторизуйтесь'


def check_user(login: str, password: str) -> tuple[bool, int]:
    '''
    Функция проверки наличия логина и пароля в базе
    '''
    current_engine = get_db_alch()
    with Session(current_engine) as session:
        stmt = select(UsersTable).where(UsersTable.name == login)
        result = session.execute(stmt)
        result = result.all()
        # если нашлась не одна запись, а другое количество, то ошибка
        if len(result) != 1:
            return False, 0
        # Если логин и пароль соответствуют тому что в базе, то успех
        elif login == result[0][0].name and hash_password(password) == result[0][0].password:
            return True, result[0][0].id
        #  других случая ошибка
        else:
            return False, 0


def add_asset(asset: str, amount: str, month, user_id) -> tuple[bool, str]:
    """
    Добавление актива
    """
    current_engine = get_db_alch()
    with (Session(current_engine) as session):
        new_asset = AssetsTable(
            name=asset,
            amount=amount,
            date=month,
            id_user=user_id
        )
        session.add_all([new_asset])
        session.commit()
        return True, 'Актив успешно добавлен'


def get_assets(user_id: int, date: str = None) -> list:
    '''
    Возврат активов.
    Если дата заполнена, то за дату, иначе все
    '''
    current_engine = get_db_alch()
    with (Session(current_engine) as session):
        if date is not None:
            stmt = (
                select(AssetsTable)
                .where(AssetsTable.date == date)
                .where(AssetsTable.id_user == user_id)
            )
        else:
            stmt = (
                select(AssetsTable)
                .where(AssetsTable.id_user == user_id)
            )
        result = session.execute(stmt)
        result = result.all()
        print(result)
        print(type(result))
        return result

if __name__ == '__main__':
    print(check_user('asd'))