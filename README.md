# Whooing API

## iOS Web hook

iOS 웹훅을 사용하면, 전달받은 문자에 대해서 웹 API를 호출할 수 있다.
이걸 사용하면 whooing의 웹훅으로 메시지를 보낼 수 있고, whooing 내부 구현으로
보낸 메시지를 해석해서 적절한 입력을 _준비_해준다. 즉, 이 입력을 한 번 (사용자가)
가공해서 실제 거래 내역으로 입력할 수 있게 해준다.

예를 들어 내가 몇 번 해본 입력이지만, whooing은 그것의 분류를 거의 기억하지 못하기 때문에,
"한국자동차환경협회" 결제에 대해서 "충전" / "차량관련 결제"라는 것을 처리해주지 못하고 있다.

## 떠오른 생각

근데 내가 입력하는 대부분은 _과거에 입력해본_, 혹은 자주 입력해볼 것의 비율이 압도적으로 높다.
그러면 이것들에 대해서 한 번 더 처리하는 규칙을 만들면 어떨까?

* iPhone에서 내가 만든 web API를 호출하고, 이 web API가 whooing API 토큰으로 보내는 식으로 만들 수 있다.
*	이 때 내가 주로 쓰는 결제 내역들에 대해선 알아서 처리해줄 수도 있고, 뭔지 모르겠으면 지금처럼 처리하게
	넘겨버릴 수 있다.
* 외환 결제의 경우에도 짐작 가능한 경우 -- *`.` 이 들어간걸 다 USD로 처리해도 될 것 같고* -- 잘 처리할
  수 있다.
