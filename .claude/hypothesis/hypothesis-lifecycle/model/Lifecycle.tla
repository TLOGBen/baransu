---------------------------- MODULE Lifecycle ----------------------------
(* 假說的生命週期。來源：.claude/think/formal-hypothesis.md（第三版，含      *)
(* 「綠燈遇過期算紅燈」與「新舊目錄不並存」兩個決定）。                     *)
(* 每個動作與規則都引用計畫書的段落（plan:「…」）。                          *)
EXTENDS Naturals

CONSTANTS Guard,         \* TRUE = 過期就拒答；FALSE = 8.15.0 現況
          MaxChanges,    \* 來源最多改幾次
          GreenMode,     \* "red" = 綠燈遇過期算紅燈（已決定）；"warn" = 只提醒
          AllowBoth,     \* TRUE = 允許新舊目錄並存；FALSE = 不並存（已決定）
          MarkMigrated,  \* TRUE = 搬來的假說標「嚴格檢查未完成」（已決定）
          DeclareNeedsCurrent, \* TRUE = 宣告完成只認對目前版本的通過（改壞版本：FALSE）
          AllowDeclare   \* TRUE = 有「宣告完成」這一步（看過它成功：FALSE 時目標應走不到）

Readers == {"proveit", "review", "green"}

VARIABLES srcVer,    \* 來源目前的版本
          srcBug,    \* 來源目前是否違反性質
          loc,       \* "none" | "old" | "new" | "both"：這個區塊的假說在哪裡
          syncVer,   \* 新目錄那份（/hypothesis 維護的）同步點
          modelBug,  \* 新目錄那份模型看到的結果
          oldSync,   \* 舊目錄那份（沒有人維護）的同步點
          oldBug,    \* 舊目錄那份模型看到的結果
          checked,   \* 讀者用的那份，是否真的做過「看過它成功」
          rep, repVer,
          greenOk,   \* 綠燈對目前版本放行了嗎
          readOld,   \* 是否有讀者在新目錄存在時讀了舊目錄
          done

vars == <<srcVer, srcBug, loc, syncVer, modelBug, oldSync, oldBug, checked,
          rep, repVer, greenOk, readOld, done>>

Init ==
  /\ srcVer = 0
  /\ srcBug \in BOOLEAN
  /\ loc \in {"none", "old"}          \* 專案可能已有 8.15.0 的舊檢查
  /\ syncVer = 0 /\ modelBug = FALSE
  /\ oldSync = 0 /\ oldBug = srcBug
  /\ checked = FALSE
  /\ rep = [r \in Readers |-> "none"] /\ repVer = [r \in Readers |-> 0]
  /\ greenOk = FALSE /\ readOld = FALSE /\ done = FALSE

\* /hypothesis 寫下新區塊：看過失敗、看過成功 (plan:「看過它失敗」「看過它成功」)
Write ==
  /\ \/ loc = "none"
     \/ AllowBoth /\ loc = "old"      \* 決定 C：不並存時，舊的還在就不能寫
  /\ loc' = IF loc = "old" THEN "both" ELSE "new"
  /\ syncVer' = srcVer /\ modelBug' = srcBug /\ checked' = TRUE
  /\ UNCHANGED <<srcVer, srcBug, oldSync, oldBug, rep, repVer, greenOk, readOld, done>>

\* 搬家：一次完整移動 (plan:「搬家是一次完整的移動，不是複製」)
Migrate ==
  /\ loc = "old"
  /\ loc' = "new"
  /\ syncVer' = oldSync /\ modelBug' = oldBug
  /\ checked' = FALSE                 \* 8.15.0 的檢查沒做過「看過它成功」
  /\ UNCHANGED <<srcVer, srcBug, oldSync, oldBug, rep, repVer, greenOk, readOld, done>>

Change ==
  /\ srcVer < MaxChanges
  /\ srcVer' = srcVer + 1 /\ srcBug' \in BOOLEAN
  /\ greenOk' = FALSE /\ done' = FALSE
  /\ UNCHANGED <<loc, syncVer, modelBug, oldSync, oldBug, checked, rep, repVer, readOld>>

Verdict(s, b) == IF Guard /\ s /= srcVer THEN "stale" ELSE IF b THEN "fail" ELSE "pass"

\* 讀者重跑。兩份並存時，讀者可能讀到任一份 (plan:「以哪一個為準」原本沒寫)
Check(r) ==
  /\ loc /= "none"
  /\ \E c \in (IF loc = "both" THEN {"old", "new"} ELSE IF loc = "old" THEN {"old"} ELSE {"new"}) :
       LET v == IF c = "old" THEN Verdict(oldSync, oldBug) ELSE Verdict(syncVer, modelBug) IN
       /\ rep' = [rep EXCEPT ![r] = v]
       /\ repVer' = [repVer EXCEPT ![r] = srcVer]
       /\ readOld' = (readOld \/ (loc = "both" /\ c = "old"))
       /\ greenOk' = IF r /= "green" THEN greenOk
                     ELSE (v = "pass") \/ (GreenMode = "warn" /\ v = "stale")
  /\ UNCHANGED <<srcVer, srcBug, loc, syncVer, modelBug, oldSync, oldBug, checked, done>>

\* --maintain：照來源更新新目錄那份，補做「看過它成功」 (plan:「維護」)
Maintain ==
  /\ loc \in {"new", "both"}
  /\ (syncVer /= srcVer \/ ~checked)
  /\ syncVer' = srcVer /\ modelBug' = srcBug /\ checked' = TRUE
  /\ UNCHANGED <<srcVer, srcBug, loc, oldSync, oldBug, rep, repVer, greenOk, readOld, done>>

\* 宣告完成 (plan:「完成 = 假說 X 被證明」；搬來的要先補完嚴格檢查)
Declare ==
  /\ AllowDeclare
  /\ ~done
  /\ rep["proveit"] = "pass"
  /\ (DeclareNeedsCurrent => repVer["proveit"] = srcVer)
  /\ (MarkMigrated => checked)
  /\ done' = TRUE
  /\ UNCHANGED <<srcVer, srcBug, loc, syncVer, modelBug, oldSync, oldBug, checked,
                 rep, repVer, greenOk, readOld>>

Next == Write \/ Migrate \/ Change \/ Maintain \/ Declare \/ \E r \in Readers : Check(r)

SpecManual == Init /\ [][Next]_vars /\ WF_vars(Write) /\ WF_vars(Declare)
              /\ \A r \in Readers : WF_vars(Check(r))
SpecAuto   == SpecManual /\ WF_vars(Maintain) /\ WF_vars(Migrate)

-----------------------------------------------------------------------------
\* S1 讀者對目前版本說「通過」，目前版本就沒有問題
NoFalsePass  == \A r \in Readers : (rep[r] = "pass" /\ repVer[r] = srcVer) => ~srcBug
\* S2 宣告完成時，目前版本沒有問題
DoneSound    == done => ~srcBug
\* S3 綠燈放行時，目前版本沒有問題（決定：過期算紅燈）
GreenSound   == greenOk => ~srcBug
\* S4 新目錄存在時，沒有讀者去讀沒人維護的舊目錄（決定：不並存）
ReadsMaintained == ~readOld
\* S5 宣告完成用的那份，真的做過「看過它成功」（決定：搬來的先標未完成）
DoneStrict   == done => checked
\* G1 「完成」走得到
NeverDone    == ~done
\* L1 寫下或搬來之後，同步點終究追上來源，而且嚴格檢查補完
EventuallyInSync == [](loc \in {"new", "both"} => <>(syncVer = srcVer /\ checked))
=============================================================================
