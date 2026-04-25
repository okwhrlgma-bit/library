# Excel 연동 가이드 (사서용)

> "Excel에서 ISBN만 입력하면 도서 정보가 자동으로 채워졌으면 좋겠어요" — 모든 사서

kormarc-auto는 사서가 익숙한 Excel을 그대로 쓸 수 있도록 **3가지 방법**을 제공합니다. 코딩 지식 없이도 가능한 것부터 순서대로 정리했습니다.

---

## 방법 1. CLI 일괄 처리 (가장 쉬움) ★★★

### 1단계: 빈 템플릿 받기
```powershell
kormarc-auto xlsx template --output 신착도서.xlsx
```

### 2단계: Excel에서 A열에 ISBN 채우기
A열에 ISBN을 한 줄에 하나씩 입력 (978로 시작하는 13자리). 1행은 헤더, 2행부터 데이터.

| ISBN (필수) | 표제 | 저자 | … |
|---|---|---|---|
| 9788936434120 | | | |
| 9788932020789 | | | |

### 3단계: 자동 채우기
```powershell
kormarc-auto xlsx fill 신착도서.xlsx --output 완성.xlsx
```

→ 표제·저자·발행자·KDC·청구기호·신뢰도·출처가 자동으로 들어갑니다.

---

## 방법 2. Excel Power Query (REST API 직접 호출) ★★

서버를 띄워 두고(`kormarc-auto serve`) Excel에서 ISBN을 입력하면 즉시 채워집니다.

### Power Query M 코드

`데이터` → `데이터 가져오기` → `기타 원본` → `빈 쿼리` → 고급 편집기 열기 → 다음 붙여넣기:

```m
let
    BaseUrl = "http://localhost:8000/isbn",
    ApiKey = "kma_demo_xxxxxxxxxxxxxxxxxxxxxx",  // .env의 KORMARC_DEMO_KEY
    FetchByIsbn = (isbn as text) =>
        let
            Response = Web.Contents(
                BaseUrl,
                [
                    Headers = [
                        #"X-API-Key" = ApiKey,
                        #"Content-Type" = "application/json"
                    ],
                    Content = Text.ToBinary("{""isbn"":""" & isbn & """}")
                ]
            ),
            Json = Json.Document(Response)
        in
            Json,

    // 사용 예: ISBN 시트의 A열을 읽어 처리
    Source = Excel.CurrentWorkbook(){[Name="ISBNs"]}[Content],
    Filled = Table.AddColumn(Source, "Result", each FetchByIsbn([ISBN])),
    Expanded = Table.ExpandRecordColumn(
        Filled, "Result",
        {"title", "author", "publisher", "publication_year", "confidence"},
        {"표제", "저자", "발행자", "발행연도", "신뢰도"}
    )
in
    Expanded
```

`ISBNs`라는 이름의 표 정의가 필요 (Ctrl+T로 표 변환 후 `테이블 디자인`에서 이름 변경).

⚠ **방화벽**: 첫 호출 시 Excel이 외부 호출 권한을 요청 — 무시(익명 액세스) 선택.

---

## 방법 3. VBA 매크로 (오프라인·옛 Excel 호환) ★

Excel 2010 이상. `Alt+F11` → 새 모듈에 다음 붙여넣기:

```vb
Function KormarcLookup(isbn As String) As String
    Dim http As Object, url As String, body As String
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = "http://localhost:8000/isbn"
    body = "{""isbn"":""" & isbn & """}"

    http.Open "POST", url, False
    http.setRequestHeader "X-API-Key", "kma_demo_xxxxxxxxxxxxxxxxxxxxxx"
    http.setRequestHeader "Content-Type", "application/json"
    http.send body

    If http.Status = 200 Then
        ' 매우 단순 파싱 — 표제만 추출 (jsonconverter.bas 추가 권장)
        Dim s As String
        s = http.responseText
        KormarcLookup = ExtractField(s, """title"":""")
    Else
        KormarcLookup = "(오류 " & http.Status & ")"
    End If
End Function

Private Function ExtractField(json As String, key As String) As String
    Dim p As Long, q As Long
    p = InStr(json, key)
    If p = 0 Then Exit Function
    p = p + Len(key)
    q = InStr(p, json, """")
    ExtractField = Mid(json, p, q - p)
End Function
```

셀에 `=KormarcLookup(A2)` — A2 ISBN의 표제 자동 채움.

---

## Claude Desktop / Claude Code MCP 연동

Claude Desktop이나 Claude Code에서 Excel 파일을 직접 분석·편집하고 싶다면:

1. `kormarc-server`를 로컬에서 띄워 두기
2. Claude에게 부탁:
   > "C:\\작업\\신착도서.xlsx 파일을 열어서 A열의 ISBN을 모두 `http://localhost:8000/isbn` REST API로 조회한 후 표제·저자·KDC를 B·C·D 열에 채워줘"

Claude Code는 위 방법1 (`kormarc-auto xlsx fill`) 명령을 자동으로 실행해 줍니다.

---

## FAQ

**Q. ISBN을 모를 때는?**
A. 표제·저자로 검색: `kormarc-auto search "한강 작별"` → 후보 중 ISBN 선택 → 위 방법으로 일괄 처리.

**Q. 회사 PC가 외부망 차단인데?**
A. 방법 1(CLI)은 인터넷이 필요하지만 ISBN→메타데이터 호출만. KOLAS 반입 직전 단계. 방법 3(VBA)은 사내 서버에 `kormarc-server`를 두면 외부망 없이도 됨.

**Q. 결과 정확도는?**
A. 국립중앙도서관 1순위 + 다른 소스 폴백. 평균 신뢰도 0.85+. 사서 검토 필수.

---

## 가격 안내

- **무료 50건**: 가입 즉시 (`kormarc-auto signup`)
- **권당 100원** 또는 **월 정액**: `docs/pricing.md` 참조
