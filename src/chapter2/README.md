# Chapter 2. 저장소 패턴

<aside>
💡 **저장소 패턴**은 데이터 저장소를 더 간단히 추상화한 것으로 이 패턴을 사용하면 **모델 계층과 데이터 계층을 분리**할 수 있다. 이런 간략한 추상화가 어떻게 DB의 복잡성을 감춰 시스템을 테스트하기 좋게 만드는지 구체적인 예제로 살펴본다.

</aside>

다음 그림은 만들려는 시스템을 미리 보여준다. Repository 객체는 도메인 모델과 DB 사이에 존재한다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/84eee4a1-0e69-4316-a036-1a3708994c4f/Untitled.png)

### 도메인 모델 영속화

여기서는 웹 API가 MVP(minimum viable product) 된다. end to end 테스트로 바로 들어가서 웹 프레임워크에 기능을 넣고, 외부로부터 내부 방향으로 테스트를 시작한다. 결국 **영속적인 저장소**가 필요하다.

## 2.2 의사코드: 무엇이 필요할까?

처음 API 엔드포인트를 만들 때는 보통 다음과 비슷한 코드를 작성한다.

```python
@flask.route.gubbins
def allocate_endpoint():
    # 요청으로부터 주문 라인 추출
    line = OrderLine(request.params, ...)

    # DB에서 모든 배치 가져오기
    batches = ...

    # 도메인 서비스 호출
    allocate(line, batch)

    # 아떤 방식으로든 할당한 배치를 다시 DB에 저장
    return 201
```

배치 정보를 DB에서 가져와 도메인 모델 객체를 초기화하는 방법이 필요하다. 그리고 도메인 객체 모델에 있는 정보를 DB에 저장하는 방법도 필요하다.

### 2.3 데이터 접근에 DIP 적용하기

모델을 내부에 있는 것으로 간주하고, 의존성이 내부로 들어오게 만들어야 한다. 이런 방식을 onion architecture라고 부른다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/4167c2dc-eb57-4844-bf19-c56a54313ef0/Untitled.png)

도메인 모델에는 어떠한 의존성도 없어야 이상적이다. 도우미 라이브러리에 의존하는 것은 괜찮지만, ORM이나 웹 프레임워크에 의존하는 것은 그렇지 않다. 하부 구조와 관련된 문제가 도메인 모델에 지속적으로 영향을 끼쳐서 단위 테스트를 느리게 하고 도메인 모델을 변경할 능력이 감소되는 것을 원하지 않는다.

모델을 내부에 있는 것으로 간주하고, **의존성이 내부**로 들어오게 만들어야 한다.

## 2.4 기억 되살리기: 우리가 사용하는 모델

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/08eb6602-9795-4420-88e2-3d370f0b56cb/Untitled.png)

할당은 OrderLine과 Batch를 연결하는 개념이다. 할당 정보를 Batch 객체의 컬렉션으로 저장한다.

이 모델을 관계형 데이터베이스로 번역하려면 어떻게 해야 할지 살펴보자.

### 2.4.1 일반적인 ORM 방식: ORM에 의존하는 모델

**객체 관계 매핑(ORM, object-relational mapping)**은 직접 SQL 질의를 수행하는 것이 아닌, 모델 객체를 대신해 SQL을 생성하는 프레임워크를 이용하는 것이다.

ORM이 제공하는 가장 중요한 기능은 **영속성 무지(persistence ignorance)**다. 도메인 모델이 데이터를 어떻게 적재하는지 혹은 어떻게 영속화하는지에 대해 알 필요가 없다는 의미다. 영속성 무지가 성립하면 특정 데이터베이스 기술에 도메인이 직접 의존하지 않도록 유지할 수 있다. (이런 관점에서 보면 ORM을 사용하는 것은 이미 DIP의 한 예다.)

```python
# SQLAlchemy 선언적 문법, 모델은 ORM에 의존
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Order(Base):
		id = Column(Integer, primary_key=True)

class OrderLine(Base):
		id = Column(Integer, primary_key=True)
		sku = Column(String(250))
		qty = Integer(String(250))
		order_id = Column(Integer, ForeignKey('order.id'))
		order = relationship(Order)

class Allocation(Base):
		# ...
```

모델 프로퍼티가 직접 DB 열과 연관되어 있는데 어떻게 저장소와 관련된 관심사를 모델로부터 분리할 수 있을까?

### 2.4.2 의존성 역전: 모델에 의존하는 ORM

대안은 스키마를 별도로 정의하고, 스키마와 도메인 모델을 상호 변환하는 명시적인 매퍼를 정의하는 것이다. SQLAlchemy는 이런 매퍼를 고전적 매퍼라고 부른다.

```python
#  SQLAlchemy 테이블 객체를 사용한 명시적 ORM 매핑
from sqlalchemy.orm import mapper, relationship

import model

metadata = MetaData()

order_lines = Table(
		'order_lines', metadata,
		Column('id', Integer, primary_key=True, autoincrement=True),
		Column('sku', String(250)),
		Column('qty', Integer, nullable=False),
		Column('orderid', String(255))
)

# ...

def start_mappers():
		lines_mapper = mapper(model.OrderLine, order_lines)
```

결과는 다음과 같다. start_mappers를 호출하면 쉽게 도메인 모델 인스턴스를 DB에 저장하거나 불러올 수 있다. 하지만 start_mappers를 호출하지 않으면 도메인 모델 클래스는 DB를 인식하지 못한다.

이런 구조를 사용하면 alembic(DB 마이그레이션 도구)을 통한 마이그레이션 등 SQLAlchemy의 모든 이점을 취하는 동시에 도메인 클래스를 사용해 질의를 투명하게 할 수 있다. 더 자세히 살펴보자.

처음에 ORM 설정을 할 때 ORM 설정에 대한 테스트를 작성하는 것이 유용할 수 있다. 다음 예제를 살펴보자

```python
# ORM 직접 테스트(임시 테스트)

from models import OrderLine

def test_orderline_mapper_can_load_lines(session):
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES'
        '("order1", "RED-CHAIR", 12),'
        '("order1", "RED-TABLE", 13),'
        '("order2", "BLUE-LIPSTICK", 14)'
    )

    expected = [
        OrderLine("orderl", "RED-CHAIR", 12),
        OrderLine("order1", "RED-TABLE", 13),
        OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]

    assert session.query(OrderLine).all() == expected

def test_orderline_mapper_can_save_lines(session):
    new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute('SELECT orderid, sku, qty FROM "order_lines"'))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]
```

> 파이테스트에 필요한 공통 의존성을 ‘픽스처’로 정의한다. 파이테스트는 함수 인수로 픽스처를 테스트에 주입한다. 여기서 사용하는 session 픽스처는 SQLAlchemy DB Session이다.

도메인 모델은 항상 순수한 상태를 유지하고 인프라에 신경 쓰지 않아도 된다. SQLAlchemy가 아닌 다른 ORM을 사용할 수도 있고 전혀 다른 영속화 시스템을 채택할 수도 있다. 이런 변경을 가해도 도메인 모델은 변경할 필요가 없어진다.

도메인 모델에서 수행하는 작업에 따라 객체 지향 패러다임으로부터 멀어지면 멀어질수록 ORM이 원하는 대로 작동하게 만들기가 점점 더 어려워지고 도메인 모델을 직접 바꿀 필요가 생긴다. 이제 API 엔드포인트는 다음과 같이 작성할 수 있다.

- 이전 API 엔드포인트 코드
  ```python
  @flask.route.gubbins
  def allocate_endpoint():
      # 요청으로부터 주문 라인 추출
      line = OrderLine(request.params, ...)

      # DB에서 모든 배치 가져오기
      batches = ...

      # 도메인 서비스 호출
      allocate(line, batch)

      # 아떤 방식으로든 할당한 배치를 다시 DB에 저장
      return 201
  ```

```python
@flask.route.gubbins
def allocate_endpoint():
    session = start_session()

		# 요청에서 주문 라인을 추출
		line = OrderLine(
				request.json['orderid'],
				request.json['sku'],
				request.json['qty'],
		)

		# DB에서 모든 배치를 가져옴
		batches = session.query(Batch).all()

		# 도메인 서비스를 호출
		allocate(line, batches)

		# 할당을 DB에 저장
		session.commit()

		return 201
```

## 2.5 저장소 패턴 소개

<aside>
💡 정리 X

</aside>

**저장소 패턴**은 영속적 저장소를 추상화한 것이다. 저장소 패턴은 모든 데이터가 메모리상에 존재하는 것처럼 가정해 데이터 접근과 관련된 세부 사항을 감춘다.

### 2.5.1 추상화한 저장소

가장 간단한 저장소에는 메서드가 두 가지밖에 없다. add()는 새 원소를 저장소에 추가하고, get()은 이전에 추가한 원소를 저장소에서 가져온다. 도메인과 서비스 계층에서 데이터에 접근할 때 엄격하게 이 두 가지 메서드만 사용할 수 있다. 이렇게 단순성을 강제로 유지하면 도메인 모델과 데이터베이스 사이의 결합을 끊을 수 있다.

다음은 저장소의 추상 기반 클래스(ABC)가 어떤 모양인지 보여준다,

```python
import abc
from models import Batch

class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError
```

> @abc.abstractmethod는 파이썬에서 ABC가 실제로 작동하는 몇 안 되는 요소 중 하나다. 자식 클래스가 부모 클래스에 정의된 모든 abstractmethdos를 구현하지 않으면 클래스 인스턴스화가 불가능하다.

## 2.6 테스트에 사용하는 가짜 저장소를 쉽게 만드는 방법

pass

## 2.7 파이썬에서 포트와 어댑터는 무엇인가

포트와 어댑터는 객체 지향 세계에서 나온 용어다.

- 포트: 애플리케이션과 추상화하려는 대상 사이의 **인터페이스**
- 어댑터: 인터페이스나 추상화가 뒤에 있는 **구현**

파이썬은 인터페이스를 제공하지 않기에 어댑터를 식별하기 쉽지만 포트를 정의하기는 어렵다. 추상 기반 클래스를 사용한다면 포트다. 추상 기반 클래스를 사용하지 않는다면 포트는 어댑터가 준수하고 애플리케이션이 기대하는 덕 타입일 뿐이다.

구체적으로 이번 장에서 AbstractRepository는 포트고, SqlAlchemyRepository와 FakeRepository는 어댑터다.

## 2.8 마치며

도메인이 복잡한 경우에만 이러한 아키텍처 패턴을 도입해야 한다. 이를 바탕으로 저장소 패턴과 영속성에 대해 무지한 모델의 장단점을 정리해보자.

| 장점                                                                                                                                                                                                               | 단점                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| 영속적 저장소와 도메인 모델 사이의 인터페이스를 간단하게 유지할 수 있다.                                                                                                                                           | ORM이 어느 정도 결합을 완화시켜준다. 외래키를 변경하기는 어렵지만 필요할 때 MySQL과 Postgres를 서로 바꾸기 쉽다.               |
| 모델과 인프라에 대한 사항을 완전히 분리하여 단위 테스트를 위한 가짜 저장소를 쉽게 만들 수 있고, 저장소 해법을 변경하기도 쉽다.                                                                                     | ORM 매핑을 수동으로 하려면 작업과 코드가 더 필요하다.                                                                          |
| 영속성에 대해 생각하기 전에 도메인 모델을 작성하면 처리해야 할 비즈니스 문제에 더 잘 집중할 수 있다. 접근 방식을 극적으로 바꾸고 싶을 때 외래키나 마이그레이션 등에 대해 염려하지 않고 모델에 이를 반영할 수 있다. | 간접 계층을 추가하면 유지보수 비용이 증가하고, 저장소 패턴을 본 적이 없는 파이썬 프로그래머들의 경우 WTF factor가 더 추가된다. |
| 객체를 테이블에 매핑하는 과정을 원하는 대로 제어할 수 있어 DB 스키마를 단순화할 수 있다.                                                                                                                           |                                                                                                                                |
