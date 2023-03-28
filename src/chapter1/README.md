# Part1. 도메인 모델링은 지원하는 아키텍처 구축

<aside>
💡 Part1은 TDD를 통해 풍부한 객체 모델을 만드는 방법을 살펴본다.(1장) 그후 이 모델을 기술적인 고려 사항으로부터 분리해 유지하는 방법을 살펴본다. 적극적으로 Refactoring 할 수 있도록 영속성을 모르는 코드를 만드는 방법과 도메인 주변에 안정적인 API를 만드는 방법을 보여준다.

</aside>

이 장은 4가지 핵심 설계 패턴에 대해 배운다.

- 저장소 패턴: 영속적인 저장소에 대한 추상화
- 서비스 계층 패턴: 유스 케이스의 시작과 끝을 명확하게 정의하기 위한 패턴
- 작업 단위 패턴: 원자적 연산을 제공
- 애그리게이트 패턴: 데이터 정합성을 강화하기 위한 패턴

# Chapter 1. 도메인 모델링

<aside>
💡 Chapter1은 비즈니스 프로세스를 코드로 모델링하는 방법을 배운다. TDD와 호환이 잘 되는 방식을 살펴보고, 왜 도메인 모델링이 중요한지 알오보고 도메인을 모델링하기 위한 핵심 패턴인 엔티티, 값 객체, 도메인 서비스에 대해 살펴본다.

</aside>

## 1.1 도메인 모델이란?

Chapter0에서 언급했던 비즈니스 로직 계층 (표현 계층 → 비즈니스 로직 → DB)을 앞으로는 도메인 모델이라는 용어로 사용한다.

**도메인**이란 **해결하려는 문제**를 말한다. 온라인 가구 판매회사를 예로 들면, 구매 및 조달, 제품 설계, 물류 및 배달 등 다양한 분야를 뜻할 수도 있다. 개발자 대부분은 비즈니스 프로세스를 개선하거나 자동화하기 위해 일한다. 도메인은 이런 프로세스가 지원하는 활동을 의미한다.

**모델**은 유용한 특성을 포함하는 프로세스나 현상의 지도(map)을 의미한다.

도메인 모델은 비즈니스를 수행하는 사람이 자신의 비즈니스에 대해 마음속에 가지고 있는 지도와 같다.

<aside>
💡 DDD란 간단하게 말해서, 소프트웨어에서 가장 중요한 요소는 문제에 대해 유용한 모델을 제공하도록 하는 개발론이다. 모델을 제대로 만들면 소프트웨어의 가치를 사용자에게 제공하며 새로운 일을 가능하게 해준다.
모델을 외부 제약과 최대한 무관하게 유지할 수 있고 이로 인해 모델이 더 잘 진화하고 변경될 수 있게 해주는 아키텍처를 설계해야한다.

</aside>

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/b7755ec0-9504-4c79-8f5c-9e66ceef66f0/Untitled.png)

## 1.2 도메인 언어 탐구

pass

## 1.3 도메인 모델 단위 테스트

- @dataclass decorator
  The **`@dataclass`** decorator is a feature that was introduced in Python 3.7 as part of the **`dataclasses`** module. It allows you to create classes that automatically generate some of the common special methods such as **`__init__`**, **`__repr__`**, and **`__eq__`** based on the class attributes.
  Using the **`@dataclass`** decorator can make your code more concise and easier to read. Here is an example:

  ```
  pythonCopy code
  from dataclasses import dataclass

  @dataclass
  class Person:
      name: str
      age: int
      height: float = 1.80

  ```

  In this example, we define a **`Person`** class using the **`@dataclass`** decorator. We specify the class attributes **`name`**, **`age`**, and **`height`**, and set a default value of **`1.80`** for the **`height`** attribute. The **`@dataclass`** decorator generates the **`__init__`**, **`__repr__`**, and **`__eq__`** methods for us.
  We can then create instances of the **`Person`** class like this:

  ```
  makefileCopy code
  p1 = Person("Alice", 25)
  p2 = Person("Bob", 30, 1.85)

  ```

  The **`__init__`** method automatically takes care of setting the attributes for us, based on the arguments we pass in. The **`__repr__`** method generates a string representation of the object, and the **`__eq__`** method compares two objects for equality based on their attributes.
  Note that the **`dataclasses`** module also provides other features such as default values, type annotations, and more. You can learn more about the **`dataclasses`** module in the official documentation: **[https://docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html)**

> 더 나은 타입 힌트를 얻기 위해 더 많은 타입을 사용해야 한다.
> 타입 힌트를 제대로 사용하기 위해선 `typing.NewType`으로 원시 타입을 감싸면 된다.

### **1.3.1 값 객체로 사용하기 적합한 데이터 클래스**

데이터는 있지만 유일한 식별자가 없는 비즈니스 개념이 있으면, 이를 표현 하기 위해 **값 객체**패턴을 선택하는 경우가 종종 있다. 값 객체는 안에 있는 데이터에 따라 유일하게 식별될 수 있는 도메인 객체를 의미한다. 보통 값 객체를 불변 객체(immutable object)로 만들곤 한다.

```python
# OrderLine은 값 객체
@dataclass(frozen=True)
class OrderLine:
		orderid: OrderReference
		sku: ProductReference
		qty: Quantity
```

데이터 클래스(혹은 namedtuple, 네임드 튜플)의 장점은 **값 동등성**(value equality)을 부여할 수 있다는 것이다.

- 값 객체에 대한 추가 예제

  ```python
  from dataclasses import dataclass
  from typing import NamedTuple
  from collections import namedtuple

  @dataclass(frozen=True)
  class Name:
      first_name: str
      surname: str

  class Money(NamedTuple):
      currency: str
      value: int

  Line = namedtuple('Line', ['sku', 'qty'])

  def test_equality():
      assert Money('gbp', 10) == Money('gbp', 10)
      assert Name('Harry', 'Percival') != Name('Bob', 'Gregory')
      assert Line('RED-CHAIR', 5) == Line('RED-CHAIR', 5)
  ```

### **1.3.2 값 객체와 엔티티**

주문 라인은 그 라인의 주문 ID, SKU, 수량에 의해 유일하게 식별된다. 이 세 가지 값 중 하나를 변경하면 새로운 라인이 생긴다. 이는 값 객체의 정의를 따른다. 값 객체는 내부에 있는 데이터에 의해 결정되며 오랫동안 유지되는 정체성이 존재하지 않는다. 배치는 참조 번호에 의해 구분된다.

오랫동안 유지되는 정체성이 존재하는 도메인 객체를 **엔티티**라고 한다. 값과 달리 엔티티에는 **정체성 동등성**이 있다. 예제의 Batch는 엔티티다. 라인을 배치에 할당할 수 있고 배치 도착 예정 날짜를 변경할 수도 있지만, 이런 값을 바꿔도 배치는 여전히 이전과 같은 배치다.

- **eq**
  - 파이썬의 **eq** 매직 메서드는 클래스가 == 연산자에 대해 작동하는 방식을 정의한다.
- **hash**
  - 객체를 집합에 추가하거나 딕셔너리의 키로 사용할 때 동작을 제어하기 위해 사용한다.

값 객체의 경우, 모든 값 속성을 사용해 해시를 정의하고 객체를 반드시 불변 객체로 만들어야 한다. 데이터 클래스에 대해 `@frozen=True`를 지정하면 불변 객체로 만들 수 있다.

엔티티의 경우, 가장 단순한 선택은 해시를 `None`으로 정의하는 것이다. 즉, 이 객체에 대한 해시를 계산할 수 없고 그에 따라 집합 등에서 사용할 수도 없다는 뜻이다. 특정한 이유로 엔티티를 집합에 넣거나 딕셔너리의 키로 사용해야 한다면 시간과 무관하게 엔티티의 정체성을 식별해주는 속성을 사용해 해시를 정의해야 한다. (ex: `.reference`) 그리고, 이 속성을 읽기 전용으로 만들어야 한다.

> **eq**를 변경하지 않았다면 **hash**를 변경해서는 안 된다.

## 1.4 모든 것을 객체로 만들 필요는 없다: 도메인 서비스 함수

### 1.4.1 파이썬 매직 메서드 사용 시 모델과 파이썬 숙어 함께 사용 가능

모델 클래스에서 `sorted()`가 작동하게 하려면 `__gt__`를 도메인 모델이 구현해야 한다.

### 1.4.2 예외를 사용해 도메인 개념 표현 가능

품절로 주문을 할당할 수 없는 경우를 위해 도메인 예외를 사용한다.

- p.56 도메인 모델링 정
  ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/934117a5-46c6-4457-a0f8-077e6ddf780b/Untitled.png)
