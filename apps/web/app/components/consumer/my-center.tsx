"use client";
import { Button, TextInput, Select, TextArea } from "../ui/controls";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  ArrowLeft,
  Plus,
  Plant,
  ChatCircleDots,
  Trash,
  UserCircle,
  FileText,
} from "@phosphor-icons/react";
import {
  consumerApi,
  dateLabel,
  type Industry,
  type PublicReport,
  type Conversation,
} from "./api";
import ReportList from "./report-list";
import Tracking from "./tracking";
import Dashboard from "../../dashboard/workbench";
type Report = {
  report_id: string;
  title: string;
  label: string;
  created_at: string;
};
export default function MyCenter() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [bookmarks, setBookmarks] = useState<PublicReport[]>([]);
  const [publications, setPublications] = useState<PublicReport[]>([]);
  const [chats, setChats] = useState<Conversation[]>([]);
  const [privateReports, setPrivateReports] = useState<Report[]>([]);
  const [links, setLinks] = useState<
    { report_id: string; industry_id: string }[]
  >([]);
  const [tab, setTab] = useState("industries");
  const [selected, setSelected] = useState<Industry | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [publicationMore, setPublicationMore] = useState(false);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState<Industry | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [domain, setDomain] = useState("technology");
  const [confirm, setConfirm] = useState<Industry | null>(null);
  const [removal, setRemoval] = useState<{
    kind: "industry" | "chat";
    id: string;
    name: string;
  } | null>(null);
  async function load() {
    setError("");
    try {
      const [i, b, p, c, r, l] = await Promise.all([
        consumerApi<Industry[]>("account/me/community/industries"),
        consumerApi<PublicReport[]>("account/me/community/bookmarks"),
        consumerApi<PublicReport[]>("account/me/community/publications"),
        consumerApi<Conversation[]>("account/me/conversations"),
        consumerApi<Report[]>("account/reports"),
        consumerApi<{ report_id: string; industry_id: string }[]>(
          "account/me/community/private-reports",
        ),
      ]);
      setIndustries(i);
      setBookmarks(b);
      setPublications(p);
      setPublicationMore(p.length === 24);
      setChats(c);
      setPrivateReports(r);
      setLinks(l);
      setSelected((current) =>
        current ? i.find((row) => row.id === current.id) || null : null,
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    void load();
    if (new URLSearchParams(window.location.search).get("create"))
      setCreating(true);
  }, []);
  async function morePublications() {
    setBusy(true);
    setError("");
    try {
      const rows = await consumerApi<PublicReport[]>(
        `account/me/community/publications?offset=${publications.length}`,
      );
      setPublications((current) => [...current, ...rows]);
      setPublicationMore(rows.length === 24);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function action(fn: () => Promise<void>) {
    if (busy) return;
    setBusy(true);
    setNotice("");
    setError("");
    try {
      await fn();
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function edit(industry: Industry) {
    setEditing(industry);
    setCreating(true);
    setName(industry.name);
    setDescription(industry.description);
    setDomain(industry.domain);
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    await action(async () => {
      await consumerApi(
        `account/me/community/industries${editing ? `/${editing.id}` : ""}`,
        editing ? "PUT" : "POST",
        { name, description, domain },
      );
      setCreating(false);
      setEditing(null);
      setName("");
      setDescription("");
      setTab("industries");
      setNotice(editing ? "行业信息已更新。" : "行业已创建，默认仅自己可见。");
    });
  }
  const currentChats = selected
    ? chats.filter((c) => c.industry_id === selected.id)
    : chats;
  const currentReports = selected
    ? privateReports.filter(
        (r) =>
          links.some(
            (l) => l.report_id === r.report_id && l.industry_id === selected.id,
          ) ||
          chats.some(
            (c) => c.industry_id === selected.id && c.report_id === r.report_id,
          ),
      )
    : privateReports;
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">个人中心</p>
          <div className="my-intro">
            <UserCircle size={42} weight="duotone" />
            <h1>我的未来观察</h1>
          </div>
          <p>把感兴趣的行业、研究与发现，慢慢积累在这里。</p>
        </div>
        <div className="heading-actions">
          <Button
            className="secondary"
            onClick={() => {
              setCreating(!creating);
              setEditing(null);
              setName("");
              setDescription("");
            }}
          >
            <Plus size={17} /> 添加行业
          </Button>
          <Link className="button" href="/chat">
            <ChatCircleDots size={18} /> 发起研究
          </Link>
        </div>
      </div>
      <div className="personal-quick-links">
        <Link href="/settings">画像与隐私</Link>
        <Link href="/notifications">通知与订阅</Link>
        <Link href="/account/security">账号安全</Link>
        <Link href="/billing">套餐与账单</Link>
      </div>
      {notice && (
        <p className="inline-notice" role="status">
          {notice}
        </p>
      )}
      {error && (
        <div className="inline-notice">
          <p role="alert">{error}</p>
          <Button className="quiet" onClick={load}>
            重新加载
          </Button>
        </div>
      )}
      {creating && (
        <form className="create-industry-form" onSubmit={submit}>
          <h2>{editing ? "编辑行业" : "创建一个自己的行业"}</h2>
          <p>先为自己保存。你可以稍后选择是否公开这个行业。</p>
          <label htmlFor="custom-industry-name">行业名称</label>
          <TextInput
            id="custom-industry-name"
            required
            maxLength={60}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="例如：AI 与教育"
          />
          <label htmlFor="custom-industry-domain">所属方向</label>
          <Select
            id="custom-industry-domain"
            value={domain}
            onValueChange={(e) => setDomain(e)}
          >
            {Object.entries({
              technology: "信息技术",
              energy: "新能源",
              healthcare: "医疗健康",
              manufacturing: "先进制造",
              education: "教育与学习",
              finance: "金融服务",
              services: "生活服务",
              society: "社会变化",
            }).map(([v, t]) => (
              <option key={v} value={v}>
                {t}
              </option>
            ))}
          </Select>
          <label htmlFor="custom-industry-description">我想关注什么</label>
          <TextArea
            id="custom-industry-description"
            required
            maxLength={300}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="简单说说你希望观察的范围。"
          />
          <div className="form-actions">
            <Button disabled={busy || !name.trim() || !description.trim()}>
              {busy ? "正在保存…" : editing ? "保存修改" : "创建行业"}
            </Button>
            <Button
              className="quiet"
              type="button"
              onClick={() => setCreating(false)}
            >
              取消
            </Button>
            <Link href="/industries">从公开行业中添加</Link>
          </div>
        </form>
      )}
      {selected && (
        <div className="industry-management">
          <Button
            className="quiet"
            onClick={() => {
              setSelected(null);
              setTab("industries");
            }}
          >
            <ArrowLeft size={15} /> 我的全部行业
          </Button>
          <h2 style={{ marginTop: 20 }}>{selected.name}</h2>
          <p>{selected.description}</p>
          <div className="form-actions">
            <Link className="button" href={`/chat?industry=${selected.id}`}>
              研究这个行业 <ArrowRight size={16} />
            </Link>
            {selected.public && (
              <Link
                className="button secondary"
                href={`/industries/${selected.id}`}
              >
                查看公开报告
              </Link>
            )}
            {selected.owned && (
              <Button className="secondary" onClick={() => edit(selected)}>
                编辑行业
              </Button>
            )}
            {selected.owned && (
              <Button className="quiet" onClick={() => setConfirm(selected)}>
                {selected.public ? "撤回行业公开" : "公开这个行业"}
              </Button>
            )}
          </div>
        </div>
      )}
      {selected?.owned && (
        <Tracking key={selected.id} industryId={selected.id} />
      )}
      {selected?.source_industry_id && (
        <p className="public-source-note">
          这是你的独立行业，编辑不会影响原公开行业。{" "}
          <Link href={`/industries/${selected.source_industry_id}`}>
            查看来源行业与公开报告
          </Link>
        </p>
      )}
      {confirm && (
        <div className="confirm-box">
          <h3>{confirm.public ? "撤回行业公开？" : "公开这个行业？"}</h3>
          <p>
            {confirm.public
              ? "公开发现页将不再展示该行业及其报告；已添加行业的人仍可保留行业入口。报告不会自动变为私有，请在我的公开内容中单独管理。"
              : "其他人可以看到行业名称和简介，并添加到自己的行业。其下的私人报告和聊天记录不会一起公开。"}
          </p>
          <div className="form-actions">
            <Button
              disabled={busy}
              onClick={() =>
                action(async () => {
                  await consumerApi(
                    `account/me/community/industries/${confirm.id}/visibility`,
                    "PUT",
                    { public: !confirm.public },
                  );
                  setConfirm(null);
                  setNotice("行业公开设置已更新。");
                })
              }
            >
              确认{confirm.public ? "撤回" : "公开"}
            </Button>
            <Button className="quiet" onClick={() => setConfirm(null)}>
              取消
            </Button>
          </div>
        </div>
      )}
      {removal && (
        <div className="confirm-box" role="region" aria-label="确认内容操作">
          <h3>
            {removal.kind === "industry"
              ? "从我的行业中移除？"
              : "删除这段研究对话？"}
          </h3>
          <p>{removal.name}</p>
          <p>
            {removal.kind === "industry"
              ? "已有报告、收藏和研究对话仍保留；你创建并公开的行业不会因此撤回。"
              : "未完成的任务会取消，已完成的报告仍保留。对话删除后无法恢复。"}
          </p>
          <div className="form-actions">
            <Button
              disabled={busy}
              onClick={() =>
                action(async () => {
                  await consumerApi(
                    removal.kind === "industry"
                      ? `account/me/community/industries/${removal.id}/membership`
                      : `account/me/conversations/${removal.id}`,
                    "DELETE",
                  );
                  setNotice(
                    removal.kind === "industry"
                      ? "已移除行业，原有内容仍保留。"
                      : "对话已删除。",
                  );
                  setRemoval(null);
                })
              }
            >
              确认{removal.kind === "industry" ? "移除" : "删除对话"}
            </Button>
            <Button className="quiet" onClick={() => setRemoval(null)}>
              取消
            </Button>
          </div>
        </div>
      )}
      <div className="consumer-tabs" role="tablist" aria-label="我的内容">
        {[
          ["industries", "我的行业"],
          ["reports", "我的报告"],
          ["saved", "我的收藏"],
          ["shared", "我的公开内容"],
          ["chats", "研究对话"],
        ].map(([value, label]) => (
          <Button
            key={value}
            role="tab"
            aria-selected={tab === value}
            className={tab === value ? "selected" : ""}
            onClick={() => setTab(value)}
          >
            {label}
          </Button>
        ))}
      </div>
      {loading ? (
        <div className="skeleton hero-skeleton" aria-label="正在加载我的内容" />
      ) : (
        <>
          {tab === "industries" &&
            (selected ? (
              <>
                <h2>这个行业的报告</h2>
                {currentReports.length ? (
                  <div className="private-report-list">
                    {currentReports.map((r) => (
                      <Link
                        key={r.report_id}
                        className="private-report-row"
                        href={`/reports/${r.report_id}`}
                      >
                        <FileText size={22} />
                        <div>
                          <h3>{r.title}</h3>
                          <p>{dateLabel(r.created_at)} · 仅自己可见</p>
                        </div>
                        <ArrowRight size={18} />
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <h3>还没有自己的报告</h3>
                    <p>
                      从一次研究对话开始，也可以在“我的报告”中把已有报告归到这里。
                    </p>
                    <Link href={`/chat?industry=${selected.id}`}>开始研究</Link>
                  </div>
                )}
                <h2 style={{ marginTop: 32 }}>收藏到这个行业</h2>
                <ReportList
                  reports={bookmarks.filter(
                    (b) => b.saved_industry_id === selected.id,
                  )}
                />
                <h2 style={{ marginTop: 32 }}>这个行业的研究对话</h2>
              </>
            ) : (
              <div className="industry-grid">
                {industries.map((industry) => (
                  <div className="industry-tile" key={industry.id}>
                    <Plant className="tile-icon" size={26} />
                    <h2>
                      <Link
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          setSelected(industry);
                        }}
                      >
                        {industry.name}
                      </Link>
                    </h2>
                    <p>{industry.description}</p>
                    <div className="tile-footer">
                      <Button onClick={() => setSelected(industry)}>
                        查看报告 <ArrowRight size={14} />
                      </Button>
                      <span>
                        {industry.owned
                          ? industry.public
                            ? "我创建 · 已公开"
                            : "我创建 · 私有"
                          : "已添加"}
                      </span>
                      {industry.added ? (
                        <Button
                          aria-label={`移除${industry.name}`}
                          className="danger"
                          disabled={busy}
                          onClick={() => {
                            setConfirm(null);
                            setRemoval({
                              kind: "industry",
                              id: industry.id,
                              name: industry.name,
                            });
                          }}
                        >
                          <Trash size={15} />
                        </Button>
                      ) : (
                        <Button
                          aria-label={`重新关注${industry.name}`}
                          disabled={busy}
                          onClick={() =>
                            action(async () => {
                              await consumerApi(
                                `account/me/community/industries/${industry.id}/membership`,
                                "PUT",
                              );
                              setNotice("已重新添加关注。");
                            })
                          }
                        >
                          <Plus size={15} />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
                {!industries.length && (
                  <div className="empty-state">
                    <Plant size={30} />
                    <h3>从一个感兴趣的行业开始</h3>
                    <p>添加公开行业，或创建自己的观察方向。</p>
                    <Link href="/industries">
                      去发现行业 <ArrowRight size={15} />
                    </Link>
                  </div>
                )}
              </div>
            ))}
          {tab === "reports" && (
            <>
              <div className="personal-legacy">
                <Dashboard />
              </div>
              {privateReports.length > 0 && (
                <section>
                  <h2>把报告整理到行业</h2>
                  {privateReports.map((r) => (
                    <div className="private-report-row" key={r.report_id}>
                      <div>
                        <h3>
                          <Link href={`/reports/${r.report_id}`}>
                            {r.title}
                          </Link>
                        </h3>
                      </div>
                      <label>
                        <span className="sr-only">{r.title}的归属行业</span>
                        <Select
                          aria-label={`${r.title}的归属行业`}
                          value={
                            links.find((l) => l.report_id === r.report_id)
                              ?.industry_id || ""
                          }
                          disabled={busy}
                          onValueChange={(e) => {
                            const id = e;
                            if (id)
                              void action(async () => {
                                await consumerApi(
                                  `account/me/community/private-reports/${r.report_id}`,
                                  "PUT",
                                  { industry_id: id },
                                );
                                setNotice("报告已归档到行业。");
                              });
                          }}
                        >
                          <option value="">选择归属行业</option>
                          {industries.map((i) => (
                            <option key={i.id} value={i.id}>
                              {i.name}
                            </option>
                          ))}
                        </Select>
                      </label>
                    </div>
                  ))}
                </section>
              )}
            </>
          )}
          {tab === "saved" &&
            (bookmarks.length ? (
              <ReportList reports={bookmarks} />
            ) : (
              <div className="empty-state">
                <h3>值得留下的发现，会在这里</h3>
                <p>阅读公开报告时，可以收藏到自己的行业。</p>
                <Link href="/">去发现报告</Link>
              </div>
            ))}
          {tab === "shared" && publicationMore && (
            <div className="load-more">
              <Button
                className="secondary"
                disabled={busy}
                onClick={morePublications}
              >
                {busy ? "正在加载…" : "加载更多公开内容"}
              </Button>
            </div>
          )}
          {tab === "shared" &&
            (publications.length ? (
              publications.map((p) => (
                <div className="private-report-row" key={p.id}>
                  <FileText size={22} />
                  <div>
                    <h3>{p.title}</h3>
                    <p>
                      {p.public ? "公开中" : "已撤回"} · {p.industry_name}
                    </p>
                  </div>
                  {p.public && (
                    <Link href={`/community/reports/${p.id}`}>查看</Link>
                  )}
                  <Button
                    className="secondary"
                    disabled={busy || !p.public}
                    onClick={() =>
                      action(async () => {
                        await consumerApi(
                          `account/me/community/publications/${p.id}`,
                          "DELETE",
                        );
                        setNotice("公开已撤回，原私人报告保留。");
                      })
                    }
                  >
                    撤回公开
                  </Button>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <h3>让有价值的研究被更多人看见</h3>
                <p>打开自己的报告，预览公开内容后再决定是否公开。</p>
                <Button className="quiet" onClick={() => setTab("reports")}>
                  查看我的报告
                </Button>
              </div>
            ))}
          {(tab === "chats" || (tab === "industries" && selected)) && (
            <div className="conversation-list">
              {currentChats.map((c) => (
                <div className="conversation-row" key={c.id}>
                  <ChatCircleDots size={24} />
                  <Link href={`/chat?id=${c.id}`}>
                    <h3>{c.title}</h3>
                    <p>
                      {dateLabel(c.created_at)} ·{" "}
                      {c.report_id
                        ? "报告已生成"
                        : c.job_status
                          ? "研究任务已提交"
                          : "对话已保存"}
                    </p>
                  </Link>
                  <Button
                    aria-label={`删除对话：${c.title}`}
                    disabled={busy}
                    onClick={() => {
                      setRemoval({ kind: "chat", id: c.id, name: c.title });
                    }}
                  >
                    <Trash size={17} />
                  </Button>
                </div>
              ))}
              {!currentChats.length && (
                <div className="empty-state">
                  <h3>你的下一个问题是什么？</h3>
                  <p>研究对话会自动保存在这里，随时回来继续。</p>
                  <Link
                    href={selected ? `/chat?industry=${selected.id}` : "/chat"}
                  >
                    和 AI 聊聊 <ArrowRight size={15} />
                  </Link>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </>
  );
}
