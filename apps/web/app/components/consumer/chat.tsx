"use client";
import { Button, Checkbox, Select, TextArea } from "../ui/controls";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  PaperPlaneTilt,
  Sparkle,
  FileText,
  ArrowUpRight,
  CheckCircle,
  MinusCircle,
  CircleNotch,
  ChatCircleDots,
} from "@phosphor-icons/react";
import {
  consumerApi,
  loginHref,
  type Industry,
  type Conversation,
} from "./api";
import ChatResearch from "./chat-research";
import { useIdentity } from "./shell";
export default function Chat() {
  const { identity, loading: authLoading } = useIdentity();
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [industry, setIndustry] = useState("");
  const [text, setText] = useState("");
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [consent, setConsent] = useState(false);
  const [scope, setScope] = useState<{
    scope: string;
    limitations: string[];
  } | null>(null);
  const [notice, setNotice] = useState("");
  const [modelAvailable, setModelAvailable] = useState(false);
  const [useModel, setUseModel] = useState(false);
  const [failedId, setFailedId] = useState("");
  const input = useRef<HTMLTextAreaElement>(null);
  const end = useRef<HTMLDivElement>(null);
  const key = useRef<string | null>(null);
  const processing = useRef(false);
  useEffect(() => {
    if (authLoading) return;
    let active = true;
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    setText((draft) => draft || params.get("question") || "");
    const choice = params.get("industry") || "";
    if (choice) setIndustry(choice);
    const personal = identity
      ? consumerApi<Industry[]>("account/me/community/industries")
      : Promise.resolve([]);
    Promise.all([personal, consumerApi<Industry[]>("community/industries")])
      .then(([mine, publiclyListed]) => {
        if (!active) return;
        const rows = new Map(mine.map((row) => [row.id, row]));
        for (const row of publiclyListed)
          if (!rows.has(row.id)) rows.set(row.id, row);
        setIndustries([...rows.values()]);
        if (!id) setIndustry(rows.has(choice) ? choice : "");
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    if (identity)
      consumerApi<{ model_available: boolean }>("account/me/chat-capabilities")
        .then((data) => {
          if (active) setModelAvailable(data.model_available);
        })
        .catch(() => {
          if (active) setModelAvailable(false);
        });
    if (id && identity)
      consumerApi<Conversation>(`account/me/conversations/${id}`)
        .then((data) => {
          if (active) {
            setConversation(data);
            setIndustry(data.industry_id ?? "");
          }
        })
        .catch((e) => {
          if (active) {
            setError(e.message);
            setFailedId(id);
          }
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    else setLoading(false);
    return () => {
      active = false;
    };
  }, [identity?.user_id, authLoading]);
  useEffect(() => {
    if (
      !conversation?.job_id ||
      !["queued", "running", "failed_retryable"].includes(
        conversation.job_status || "",
      )
    )
      return;
    let active = true;
    const timer = setInterval(() => {
      consumerApi<Conversation>(`account/me/conversations/${conversation.id}`)
        .then((data) => {
          if (active)
            setConversation((current) =>
              current?.id === data.id && current.job_id === data.job_id
                ? {
                    ...current,
                    job_status: data.job_status,
                    report_id: data.report_id,
                    error_code: data.error_code,
                  }
                : current,
            );
        })
        .catch(() => {
          if (active)
            setNotice("连接暂时中断。任务仍保存在服务端，可稍后刷新继续查看。");
        });
    }, 1800);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [conversation?.id, conversation?.job_id, conversation?.job_status]);
  useEffect(() => {
    if (conversation?.messages.length)
      end.current?.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth",
        block: "nearest",
      });
  }, [conversation?.messages.length]);
  async function send(event: React.FormEvent) {
    event.preventDefault();
    if (!text.trim() || processing.current) return;
    if (!identity) {
      const target = `/chat?industry=${industry}&question=${encodeURIComponent(text.trim())}`;
      window.location.assign(loginHref(target));
      return;
    }
    setBusy(true);
    processing.current = true;
    setError("");
    key.current = key.current || crypto.randomUUID();
    try {
      const data = conversation
        ? await consumerApi<Conversation>(
            `account/me/conversations/${conversation.id}/messages`,
            "POST",
            {
              text: text.trim(),
              client_id: key.current,
              use_model: useModel,
              include_memory: useModel,
            },
          )
        : await consumerApi<Conversation>("account/me/conversations", "POST", {
            question: text.trim(),
            industry_id: industry || null,
            client_id: key.current,
            use_model: useModel,
            include_memory: useModel,
          });
      setConversation(data);
      window.history.replaceState(null, "", `/chat?id=${data.id}`);
      setText("");
      key.current = null;
      setScope(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      processing.current = false;
      setBusy(false);
      input.current?.focus();
    }
  }
  async function confirmIndustry(proposalId: string) {
    if (!conversation || processing.current) return;
    processing.current = true;
    setBusy(true);
    setError("");
    try {
      const data = await consumerApi<Conversation>(
        `account/me/conversations/${conversation.id}/industries/${proposalId}`,
        "POST",
      );
      setConversation(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      processing.current = false;
      setBusy(false);
    }
  }
  async function checkScope() {
    if (processing.current) return;
    setBusy(true);
    processing.current = true;
    setError("");
    try {
      setScope(
        await consumerApi("account/research/intake", "POST", {
          question: conversation?.title || "",
          label: "DEMO",
        }),
      );
      setConsent(false);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      processing.current = false;
      setBusy(false);
    }
  }
  async function start() {
    if (!conversation || !consent || processing.current) return;
    setBusy(true);
    processing.current = true;
    setError("");
    try {
      setConversation(
        await consumerApi<Conversation>(
          `account/me/conversations/${conversation.id}/start`,
          "POST",
          { confirm_demo_reuse: true },
        ),
      );
      setScope(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      processing.current = false;
      setBusy(false);
    }
  }
  const pending =
    !!conversation?.job_id &&
    ["queued", "running", "failed_retryable"].includes(
      conversation.job_status || "",
    );
  const failed =
    !!conversation?.job_id &&
    ["cancelled", "failed_terminal"].includes(conversation.job_status || "");
  const researchIndustries = new Map<string, Pick<Industry, "id" | "name">>(
    industries.map((item) => [item.id, item]),
  );
  for (const message of conversation?.messages ?? []) {
    const proposal = message.proposal;
    if (proposal?.industry_id && !researchIndustries.has(proposal.industry_id))
      researchIndustries.set(proposal.industry_id, {
        id: proposal.industry_id,
        name: proposal.name,
      });
  }
  if (loading)
    return (
      <div className="skeleton hero-skeleton" aria-label="正在加载研究对话" />
    );
  if (failedId)
    return (
      <div className="empty-state">
        <h1>这段对话暂时无法打开</h1>
        <p role="alert">{error}</p>
        <Link href="/chat">开启新对话</Link>
      </div>
    );
  return (
    <div className="chat-page">
      <Link className="back-link" href={conversation ? "/dashboard" : "/"}>
        <ArrowLeft size={16} /> {conversation ? "回到我的研究" : "返回发现"}
      </Link>
      {conversation ? (
        <>
          <div className="chat-header">
            <div>
              <p className="eyebrow">私有研究对话 · 自动保存</p>
              <h1>{conversation.title}</h1>
              <p>先把问题聊清楚，再把研究留下来。</p>
            </div>
            <Link className="icon-button" href="/chat" aria-label="开启新对话">
              <ChatCircleDots size={24} />
            </Link>
          </div>
          <div className="chat-messages">
            {conversation.messages.map((message, i) => (
              <div key={i} className={`chat-message ${message.role}`}>
                {message.role === "assistant" && (
                  <Sparkle size={20} weight="duotone" />
                )}
                {message.role === "assistant" ? (
                  <div className="chat-agent-message">
                    {message.source && (
                      <small>
                        {message.source === "llm"
                          ? "FutureOS Agent · DeepSeek"
                          : "FutureOS Agent · 本地引导"}
                      </small>
                    )}
                    <p>{message.text}</p>
                    {message.proposal && (
                      <div className="chat-industry-proposal">
                        <strong>{message.proposal.name}</strong>
                        {message.proposal.status === "pending" ? (
                          <Button
                            className="secondary"
                            disabled={busy}
                            onClick={() =>
                              confirmIndustry(message.proposal!.id)
                            }
                          >
                            确认添加到我的行业
                          </Button>
                        ) : (
                          <span role="status">
                            {message.proposal.status === "added"
                              ? "已添加到我的行业"
                              : "已在我的行业列表"}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <p>{message.text}</p>
                )}
              </div>
            ))}
            <div ref={end} />
          </div>
          <ChatResearch
            key={conversation.id}
            conversationId={conversation.id}
            industryId={conversation.industry_id}
            industries={[...researchIndustries.values()]}
          />
          {!conversation.job_id && !scope && (
            <div className="scope-confirmation">
              <h2>先看看，这次可以研究什么。</h2>
              <p>
                当前可体验复用已有资料的演示报告。自由提问和补充信息会保存；联网深度研究与新的预测规则待接入。
              </p>
              <Button
                className="secondary"
                disabled={busy}
                onClick={checkScope}
              >
                {busy ? "正在检查…" : "查看本次研究范围"}
              </Button>
              <Link
                className="text-action"
                style={{ marginLeft: 16 }}
                href={`/onboarding?next=${encodeURIComponent(`/chat?id=${conversation.id}`)}`}
              >
                完善行业画像
              </Link>
            </div>
          )}
          {scope && (
            <div className="scope-confirmation">
              <h2>确认范围后，再开始。</h2>
              <p>{scope.scope}</p>
              <ul>
                {scope.limitations.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
              <p>
                报告依据当前行业画像与已有研究版本生成，不会声称已回答自由提问中的新预测。使用首份免费报告权益，成功后才计入使用。
              </p>
              <label>
                <Checkbox
                  checked={consent}
                  onChange={(e) => setConsent(e.target.checked)}
                />
                我了解本次使用演示资料，不会执行新的联网搜索。
              </label>
              <div className="form-actions">
                <Button disabled={busy || !consent} onClick={start}>
                  {busy ? "正在提交…" : "生成演示报告"}
                </Button>
                <Button className="quiet" onClick={() => setScope(null)}>
                  再聊聊问题
                </Button>
                <Link href="/dashboard">查看我的报告与权益</Link>
              </div>
            </div>
          )}
          {conversation.job_id && (
            <div className="agent-progress" aria-live="polite">
              <h2>
                {pending ? (
                  <CircleNotch size={21} className="busy-icon" />
                ) : conversation.report_id ? (
                  <CheckCircle size={21} />
                ) : (
                  <MinusCircle size={21} />
                )}{" "}
                {conversation.report_id
                  ? "这次报告已完成"
                  : failed
                    ? "这次研究未完成"
                    : conversation.job_status === "queued"
                      ? "已排队，稍后开始"
                      : "正在整理你的报告"}
              </h2>
              <p>演示研究 · 复用已核实资料，本次未联网搜索</p>
              <div className="agent-stages">
                <div
                  className={`agent-stage ${conversation.report_id ? "done" : ""}`}
                >
                  <span className="stage-label">
                    {conversation.report_id ? (
                      <CheckCircle size={16} />
                    ) : (
                      <MinusCircle size={16} />
                    )}{" "}
                    资料准备
                  </span>
                  <small>
                    {conversation.report_id
                      ? "已复用固定研究版本"
                      : "使用已有资料，不另行检索"}
                  </small>
                </div>
                <div className="agent-stage">
                  <span className="stage-label">
                    <MinusCircle size={16} /> 分析推演
                  </span>
                  <small>本次未执行新预测</small>
                </div>
                <div className="agent-stage">
                  <span className="stage-label">
                    <MinusCircle size={16} /> 交叉校验
                  </span>
                  <small>沿用已有审查结果</small>
                </div>
                <div
                  className={`agent-stage ${conversation.report_id ? "done" : pending ? "active" : ""}`}
                >
                  <span className="stage-label">
                    {conversation.report_id ? (
                      <CheckCircle size={16} />
                    ) : pending ? (
                      <CircleNotch size={16} className="busy-icon" />
                    ) : (
                      <MinusCircle size={16} />
                    )}{" "}
                    生成报告
                  </span>
                  <small>
                    {conversation.report_id
                      ? "已生成"
                      : failed
                        ? "未完成"
                        : conversation.job_status === "queued"
                          ? "等待开始"
                          : "处理中"}
                  </small>
                </div>
              </div>
              <details>
                <summary>查看真实执行状态</summary>
                <p>
                  {conversation.job_status === "queued"
                    ? "任务已保存，正在等待执行。"
                    : conversation.job_status === "running"
                      ? "后台正在根据固定资料生成报告。"
                      : conversation.job_status === "succeeded"
                        ? "报告和引用版本已保存。"
                        : conversation.job_status === "failed_retryable"
                          ? "暂时遇到问题，后台将自动重试。"
                          : conversation.job_status === "cancelled"
                            ? "任务已取消，未消费权益已释放。"
                            : "任务未完成，未消费权益已释放。"}
                </p>
                {conversation.error_code && (
                  <p>问题标识：{conversation.error_code}</p>
                )}
              </details>
              {pending && (
                <Button
                  className="quiet"
                  disabled={busy}
                  onClick={async () => {
                    setBusy(true);
                    setError("");
                    try {
                      await consumerApi(
                        `account/research/jobs/${conversation.job_id}/cancel`,
                        "POST",
                        {},
                      );
                      setConversation(
                        await consumerApi(
                          `account/me/conversations/${conversation.id}`,
                        ),
                      );
                    } catch (e) {
                      setError((e as Error).message);
                    } finally {
                      setBusy(false);
                    }
                  }}
                >
                  取消本次生成
                </Button>
              )}
              {failed && (
                <p>
                  <Link href="/dashboard">返回我的内容，查看报告和权益</Link>
                </p>
              )}
            </div>
          )}
          {conversation.report_id && (
            <Link
              className="report-attachment"
              href={`/reports/${conversation.report_id}`}
            >
              <FileText size={31} weight="duotone" />
              <div>
                <h3>你的行业观察报告</h3>
                <p>打开阅读、归档到行业，或预览后选择公开。</p>
              </div>
              <ArrowUpRight size={22} />
            </Link>
          )}
        </>
      ) : (
        <div className="chat-welcome">
          <Sparkle size={40} weight="duotone" />
          <p className="eyebrow">FutureOS · 聊聊未来</p>
          <h1>你的问题，值得好好研究。</h1>
          <p>聊聊行业未来会怎么变，以及你接下来可以做什么。</p>
          <div className="chat-industry-select">
            <label htmlFor="chat-industry">研究行业（选填）</label>
            <Select
              id="chat-industry"
              value={industry}
              onValueChange={(e) => setIndustry(e)}
            >
              <option value="">在对话中说明行业</option>
              {industries.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.name}
                </option>
              ))}
            </Select>
          </div>
          <div className="prompt-suggestions">
            {[
              "AI 会怎样改变我的工作？",
              "这个行业有哪些值得关注的变化？",
              "我应该从哪些问题开始观察？",
            ].map((prompt) => (
              <Button
                key={prompt}
                onClick={() => {
                  setText(prompt);
                  input.current?.focus();
                }}
              >
                {prompt}
              </Button>
            ))}
          </div>
          <p style={{ fontSize: 12 }}>
            想把新行业放进列表，也可以直接说「帮我添加储能行业」。
          </p>
        </div>
      )}
      {error && (
        <div className="inline-notice">
          <p role="alert">{error}</p>
          {error.includes("画像") && (
            <Link
              href={`/onboarding?next=${encodeURIComponent(`/chat${conversation ? `?id=${conversation.id}` : ""}`)}`}
            >
              去完善行业画像
            </Link>
          )}
        </div>
      )}
      {notice && (
        <p className="inline-notice" role="status">
          {notice}
        </p>
      )}
      <form className="chat-composer" onSubmit={send}>
        <div>
          <TextArea
            ref={input}
            aria-label={conversation ? "继续补充研究问题" : "你想研究什么"}
            value={text}
            maxLength={1000}
            rows={2}
            placeholder={
              conversation
                ? "继续补充你的问题…"
                : "说说你想了解的行业、变化或困惑…"
            }
            onChange={(e) => {
              setText(e.target.value);
              key.current = null;
            }}
            onKeyDown={(e) => {
              if (
                e.key === "Enter" &&
                !e.shiftKey &&
                !e.nativeEvent.isComposing
              ) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <Button
            className="icon-button"
            type="submit"
            disabled={busy || authLoading || !text.trim()}
            aria-label={busy ? "正在发送" : "发送问题"}
          >
            {busy ? (
              <CircleNotch className="busy-icon" size={20} />
            ) : (
              <PaperPlaneTilt size={22} />
            )}
          </Button>
        </div>
        {identity && modelAvailable && (
          <label className="chat-model-consent">
            <Checkbox
              checked={useModel}
              disabled={busy}
              onChange={(event) => {
                setUseModel(event.target.checked);
                key.current = null;
              }}
            />
            使用 DeepSeek 回复（发送行业、近期对话及本会话提取的研究要点）
          </label>
        )}
        <small>
          {identity
            ? "对话与报告默认仅自己可见 · Enter 发送，Shift + Enter 换行"
            : "登录后继续。你输入的问题会保留。"}
        </small>
      </form>
    </div>
  );
}
