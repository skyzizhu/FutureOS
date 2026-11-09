"use client";

import type { ChatResearchViewV1 } from "@futureos/contracts";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button, Select } from "../ui/controls";
import { consumerApi, type Industry } from "./api";

const active = (run: ChatResearchViewV1) =>
  ["queued", "running", "failed_retryable"].includes(run.status);
const stageLabels = {
  search: "检索行业动态",
  analysis: "分析与补证",
  report: "生成草稿",
};

export default function ChatResearch({
  conversationId,
  industryId,
  industries,
}: {
  conversationId: string;
  industryId: string | null;
  industries: Pick<Industry, "id" | "name">[];
}) {
  const endpoint = `account/me/conversations/${conversationId}/industry-research`;
  const [runs, setRuns] = useState<ChatResearchViewV1[]>([]);
  const [detail, setDetail] = useState<ChatResearchViewV1 | null>(null);
  const [selected, setSelected] = useState(industryId ?? "");
  const [horizon, setHorizon] = useState("180");
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const key = useRef<string | null>(null);
  const running = runs.find(active);
  const reload = useCallback(async () => {
    setRuns(await consumerApi<ChatResearchViewV1[]>(endpoint));
  }, [endpoint]);

  useEffect(() => {
    void reload().catch((err: Error) => setError(err.message));
  }, [reload]);

  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => {
      void reload().catch(() =>
        setError("暂时无法更新进度，任务已保存在服务端。"),
      );
    }, 1400);
    return () => clearInterval(timer);
  }, [reload, running?.id]);

  async function start() {
    if (!selected || busy) return;
    setBusy(true);
    setError("");
    key.current ??= crypto.randomUUID();
    try {
      const result = await consumerApi<ChatResearchViewV1>(endpoint, "POST", {
        client_id: key.current,
        industry_id: selected,
        horizon_days: Number(horizon),
        confirm_demo: true,
      });
      setRuns((rows) => [
        result,
        ...rows.filter((row) => row.id !== result.id),
      ]);
      setShowForm(false);
      setDetail(null);
      key.current = null;
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function open(run: ChatResearchViewV1) {
    setBusy(true);
    setError("");
    try {
      setDetail(await consumerApi<ChatResearchViewV1>(`${endpoint}/${run.id}`));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function cancel(run: ChatResearchViewV1) {
    setBusy(true);
    setError("");
    try {
      await consumerApi(`${endpoint}/${run.id}/cancel`, "POST");
      await reload();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section
      className="scope-confirmation chat-research-card"
      aria-label="行业研究任务"
    >
      <p className="eyebrow">行业研究 · DEMO</p>
      <h2>把问题推进到研究</h2>
      <p>用演示资料体验检索、分析与补证，以及草稿生成。结果会留在这段对话。</p>
      {!running && !showForm && (
        <Button className="secondary" onClick={() => setShowForm(true)}>
          选择研究范围
        </Button>
      )}
      {showForm && !running && (
        <div className="chat-research-scope">
          <label htmlFor="chat-run-industry">研究行业</label>
          <Select
            id="chat-run-industry"
            value={selected}
            disabled={busy}
            onValueChange={(value) => {
              setSelected(value);
              key.current = null;
            }}
          >
            <option value="">请选择行业</option>
            {industries.map((industry) => (
              <option key={industry.id} value={industry.id}>
                {industry.name}
              </option>
            ))}
          </Select>
          <label htmlFor="chat-run-horizon">预测期限</label>
          <Select
            id="chat-run-horizon"
            value={horizon}
            disabled={busy}
            onValueChange={(value) => {
              setHorizon(value);
              key.current = null;
            }}
          >
            <option value="90">未来三个月</option>
            <option value="180">未来半年</option>
            <option value="365">未来一年</option>
          </Select>
          <Button disabled={busy || !selected} onClick={start}>
            确认并运行行业研究演示
          </Button>
        </div>
      )}
      {error && <p role="alert">{error}</p>}
      {runs.map((run) => (
        <article key={run.id} className="chat-research-run">
          <strong>
            {run.industry} · {run.horizon_days} 天
          </strong>
          <p aria-live={active(run) ? "polite" : undefined}>
            {run.status === "queued"
              ? "等待开始"
              : run.status === "running"
                ? run.stages.at(-1)
                  ? stageLabels[run.stages[run.stages.length - 1].stage]
                  : "正在准备研究"
                : run.status === "failed_retryable"
                  ? "等待重新执行"
                  : run.status === "succeeded"
                    ? "研究已结束"
                    : run.status === "cancelled"
                      ? "已取消"
                      : "研究未完成"}
          </p>
          {run.stages.length > 0 && (
            <ol aria-label="实际执行阶段">
              {run.stages.map((stage) => (
                <li key={stage.stage}>{stageLabels[stage.stage]}</li>
              ))}
            </ol>
          )}
          {active(run) && (
            <Button
              className="quiet"
              disabled={busy}
              onClick={() => cancel(run)}
            >
              取消行业研究
            </Button>
          )}
          {run.status === "succeeded" && (
            <Button
              className="secondary"
              disabled={busy}
              onClick={() => open(run)}
            >
              查看研究结果
            </Button>
          )}
          {detail?.id === run.id && detail.result && (
            <div className="chat-research-result">
              <p className="eyebrow">DEMO · 研究草稿</p>
              {detail.result.report ? (
                <>
                  {detail.result.report.forecasts.map((forecast, index) => (
                    <section key={index}>
                      <h3>{forecast.statement}</h3>
                      <p>{forecast.mechanism}</p>
                      <p>观察信号 · {forecast.expected_signal}</p>
                      <p>证伪条件 · {forecast.falsifier}</p>
                      <p>不确定性 · {forecast.uncertainty}</p>
                    </section>
                  ))}
                  <h3>可执行的下一步</h3>
                  <ul>
                    {detail.result.report.actions.map((item, index) => (
                      <li key={index}>
                        {item.action} · {item.time_minutes} 分钟
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <p>资料不足以支持草稿。{detail.result.gaps.join("。")}</p>
              )}
              <details>
                <summary>查看使用的演示资料</summary>
                <ul>
                  {detail.result.sources.map((source) => (
                    <li key={source.source_id}>
                      {source.title} · {source.excerpt}
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          )}
        </article>
      ))}
    </section>
  );
}
