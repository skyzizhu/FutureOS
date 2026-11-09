"use client";
import { Button, Select, TextInput } from "../ui/controls";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  Plus,
  Check,
  PaperPlaneTilt,
  MagnifyingGlass,
  ArrowClockwise,
} from "@phosphor-icons/react";
import {
  consumerApi,
  loginHref,
  type Industry,
  type PublicReport,
} from "./api";
import { useIdentity } from "./shell";
import ReportList from "./report-list";
import { industryArtwork } from "./industry-banner";
export default function Discovery({ industryId }: { industryId: string }) {
  const { identity, loading: identityLoading } = useIdentity();
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [selected, setSelected] = useState<Industry | null>(null);
  const [reports, setReports] = useState<PublicReport[]>([]);
  const [membership, setMembership] = useState<{
    id: string;
    added: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [question, setQuestion] = useState("");
  const [query, setQuery] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [sort, setSort] = useState("newest");
  const [moreBusy, setMoreBusy] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const requestRef = useRef(0);
  const searchFocused = useRef(false);
  const added = membership?.id === selected?.id && membership?.added === true;
  async function loadIndustries() {
    setError("");
    try {
      const data = await consumerApi<Industry[]>("community/industries");
      setIndustries(data);
      const found = data.find((i) => i.id === industryId);
      if (found) setSelected(found);
      else if (industryId && identity)
        setSelected(
          await consumerApi<Industry>(
            `account/me/community/industries/${industryId}`,
          ),
        );
      else throw new Error("这个行业未公开或已撤回。");
    } catch (e) {
      setError((e as Error).message);
      setLoading(false);
    }
  }
  useEffect(() => {
    void loadIndustries();
    if (new URLSearchParams(window.location.search).get("search"))
      document.getElementById("report-search")?.focus();
  }, [industryId, identity?.user_id]);
  useEffect(() => {
    if (
      selected &&
      !searchFocused.current &&
      new URLSearchParams(window.location.search).get("search")
    ) {
      const field = document.getElementById("report-search");
      field?.focus();
      field?.scrollIntoView({
        block: "center",
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth",
      });
      searchFocused.current = true;
    }
  }, [selected?.id]);
  useEffect(() => {
    const timer = setTimeout(() => setSearchTerm(query), 250);
    return () => clearTimeout(timer);
  }, [query]);
  useEffect(() => {
    if (!selected || identityLoading) return;
    const id = ++requestRef.current;
    setLoading(true);
    setError("");
    const path = identity ? "account/me/community/feed" : "community/reports";
    consumerApi<PublicReport[]>(
      `${path}?q=${encodeURIComponent(searchTerm)}&sort=${sort}&industry_id=${selected.id}`,
    )
      .then((data) => {
        if (id === requestRef.current) {
          setReports(data);
          setHasMore(data.length === 24);
        }
      })
      .catch((e) => {
        if (id === requestRef.current) setError(e.message);
      })
      .finally(() => {
        if (id === requestRef.current) setLoading(false);
      });
    if (identity)
      consumerApi<Industry[]>("account/me/community/industries")
        .then((data) => {
          if (id !== requestRef.current) return;
          setMembership({
            id: selected.id,
            added: data.some(
              (item) =>
                (item.id === selected.id ||
                  item.source_industry_id === selected.id) &&
                item.added,
            ),
          });
        })
        .catch(() => {});
    else setMembership(null);
  }, [selected, identity?.user_id, identityLoading, searchTerm, sort]);
  async function loadMore() {
    if (!selected || moreBusy) return;
    const id = requestRef.current;
    setMoreBusy(true);
    setError("");
    try {
      const path = identity ? "account/me/community/feed" : "community/reports";
      const data = await consumerApi<PublicReport[]>(
        `${path}?offset=${reports.length}&q=${encodeURIComponent(searchTerm)}&sort=${sort}&industry_id=${selected.id}`,
      );
      if (id === requestRef.current) {
        setReports((current) => [
          ...current,
          ...data.filter(
            (row) => !current.some((existing) => existing.id === row.id),
          ),
        ]);
        setHasMore(data.length === 24);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setMoreBusy(false);
    }
  }
  async function add() {
    if (!selected) return;
    if (!identity) {
      window.location.assign(loginHref(`/industries/${selected.id}`));
      return;
    }
    setBusy(true);
    try {
      const owned = await consumerApi<Industry[]>(
        "account/me/community/industries",
      );
      const existing = owned.find(
        (i) => i.id === selected.id || i.source_industry_id === selected.id,
      );
      if (added && existing)
        await consumerApi(
          `account/me/community/industries/${existing.id}/membership`,
          "DELETE",
        );
      else
        await consumerApi(
          `account/me/community/industries/${selected.id}/add`,
          "PUT",
        );
      setMembership({ id: selected.id, added: !added });
      setNotice(
        added
          ? "已从我的行业中移除，原报告仍保留。"
          : "已添加为自己的行业，可独立编辑并设置监听与预测。",
      );
    } catch (e) {
      setNotice((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function ask(event: React.FormEvent) {
    event.preventDefault();
    if (!selected || !question.trim()) return;
    window.location.assign(
      `/chat?industry=${selected.id}&question=${encodeURIComponent(question.trim())}`,
    );
  }
  const visible = reports
    .filter((r) =>
      `${r.title} ${r.summary} ${r.industry_name}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    )
    .sort((a, b) =>
      sort === "recommended"
        ? 0
        : sort === "oldest"
          ? a.created_at.localeCompare(b.created_at)
          : b.created_at.localeCompare(a.created_at),
    );
  if (!selected)
    return (
      <div className="discovery-loading">
        {error ? (
          <>
            <h1>暂时没有找到这个行业</h1>
            <p role="alert">{error}</p>
            <Button onClick={loadIndustries}>
              <ArrowClockwise size={16} /> 重新加载
            </Button>
          </>
        ) : (
          <div className="skeleton hero-skeleton" aria-label="正在加载行业" />
        )}
      </div>
    );
  function selectIndustry(industry: Industry) {
    setSelected(industry);
    setSort("newest");
    setNotice("");
    setQuery("");
    setSearchTerm("");
    setLoading(true);
  }
  const industryActions = (
    <div className="hero-actions">
      <Button disabled={busy || identityLoading} onClick={add}>
        {added ? <Check size={18} /> : <Plus size={18} />}{" "}
        {busy ? "正在保存…" : added ? "已添加到我的行业" : "添加到我的行业"}
      </Button>
      <a className="text-action" href="#public-reports">
        看看大家的研究 <ArrowRight size={18} />
      </a>
    </div>
  );
  const chatEntry = (
    <form className="ask-dock" onSubmit={ask}>
      <div className="ask-intro">
        <h2>你也有想研究的问题吗？</h2>
        <p>通过对话明确问题，查看 AI 的研究过程。</p>
      </div>
      <div className="ask-input">
        <TextInput
          aria-label="你想研究的问题"
          maxLength={1000}
          required
          minLength={2}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={`聊聊你对${selected.name}行业的疑问…`}
        />
        <Button
          className="icon-button"
          aria-label="开始研究对话"
          type="submit"
          disabled={!question.trim()}
        >
          <PaperPlaneTilt size={19} />
        </Button>
      </div>
    </form>
  );
  return (
    <div className="discovery-page">
      <div className="discovery-topline">
        <p className="positioning-label">行业预测与个人决策 Agent</p>
        <h1>预测行业未来，发现下一次机遇。</h1>
        <p>让 AI 实时关注行业变化，预测未来机遇，给出与你相关的行动建议。</p>
      </div>
      <div className="industry-hero">
        <div className="industry-hero-content">
          <div className="industry-tabs" aria-label="探索行业">
            {industries.slice(0, 5).map((industry) => (
              <Button
                key={industry.id}
                className={selected.id === industry.id ? "selected" : ""}
                aria-pressed={selected.id === industry.id}
                onClick={() => {
                  if (industry.id !== selected.id) selectIndustry(industry);
                }}
              >
                {industry.name}
              </Button>
            ))}
          </div>
          <div className="hero-copy" key={selected.id}>
            <span className="tag">行业观察</span>
            <h2>{selected.name}</h2>
            <p>{selected.description}</p>
            {industryActions}
          </div>
        </div>
        <div className="industry-hero-image">
          <img
            key={selected.domain}
            src={industryArtwork(selected.domain) || "/images/industry-ai.webp"}
            alt={`${selected.name}行业主题配图`}
            fetchPriority="high"
          />
        </div>
      </div>
      {notice && (
        <p className="inline-notice" role="status">
          {notice} <Link href="/dashboard">前往我的</Link>
        </p>
      )}
      <div id="public-reports" className="feed-section">
        <div className="section-heading">
          <div>
            <h2>这个行业，大家在研究什么</h2>
          </div>
          <label className="sort-label">
            <span className="sr-only">报告排序</span>
            <Select
              aria-label="报告排序"
              value={sort}
              onValueChange={(e) => setSort(e)}
            >
              <option value="newest">最新公开</option>
              <option value="oldest">较早公开</option>
            </Select>
          </label>
        </div>
        <div className="feed-search">
          <MagnifyingGlass size={18} />
          <TextInput
            id="report-search"
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="在当前行业搜索报告"
            aria-label="搜索公开报告"
            maxLength={100}
          />
        </div>
        {error ? (
          <div className="empty-state">
            <p role="alert">{error}</p>
            <Button onClick={() => setSelected({ ...selected })}>重试</Button>
          </div>
        ) : loading || query !== searchTerm ? (
          <div className="feed-skeleton" aria-label="正在加载报告">
            <div className="skeleton" />
            <div className="skeleton" />
          </div>
        ) : visible.length ? (
          <>
            <ReportList reports={visible} />
            {hasMore && (
              <div className="load-more">
                <Button
                  className="secondary"
                  disabled={moreBusy}
                  onClick={loadMore}
                >
                  {moreBusy ? "正在加载…" : "查看更多报告"}
                </Button>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            <h3>{query ? "没有找到相关报告" : "这里还没有公开报告"}</h3>
            <p>
              {query
                ? "试试其他关键词，或者探索更多行业。"
                : "你可以添加这个行业，或者先和 AI 聊聊想研究的问题。"}
            </p>
            <Link href={`/chat?industry=${selected.id}`}>
              发起一段研究 <ArrowRight size={16} />
            </Link>
          </div>
        )}
      </div>
      {chatEntry}
    </div>
  );
}
