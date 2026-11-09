"use client";

import {
  ArrowRight,
  ArrowUpRight,
  Check,
  MagnifyingGlass,
  PaperPlaneTilt,
  Plus,
} from "@phosphor-icons/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Button, TextInput } from "../ui/controls";
import {
  consumerApi,
  loginHref,
  type Industry,
  type PublicReport,
} from "./api";
import IndustryBanner from "./industry-banner";
import ReportList from "./report-list";
import { useIdentity } from "./shell";

function useReportFeed(path: string | null) {
  const [state, setState] = useState<{
    path: string;
    reports: PublicReport[];
    error: string;
  } | null>(null);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!path) return;
    let active = true;
    consumerApi<PublicReport[]>(path)
      .then((reports) => {
        if (active) setState({ path, reports, error: "" });
      })
      .catch((error: Error) => {
        if (active) setState({ path, reports: [], error: error.message });
      });
    return () => {
      active = false;
    };
  }, [path, attempt]);
  return {
    reports: state?.path === path ? state.reports : [],
    error: state?.path === path ? state.error : "",
    loading: !!path && state?.path !== path,
    reload: () => {
      setState(null);
      setAttempt((n) => n + 1);
    },
  };
}

function Feed({
  feed,
  empty,
  showIndustry = true,
}: {
  feed: ReturnType<typeof useReportFeed>;
  empty: string;
  showIndustry?: boolean;
}) {
  if (feed.error)
    return (
      <div className="home-feed-empty">
        <p role="alert">{feed.error}</p>
        <Button className="secondary" onClick={feed.reload}>
          重试
        </Button>
      </div>
    );
  if (feed.loading)
    return (
      <div className="home-feed-loading" aria-label="正在加载报告">
        <div className="skeleton" />
        <div className="skeleton" />
      </div>
    );
  return feed.reports.length ? (
    <ReportList reports={feed.reports} compact showIndustry={showIndustry} />
  ) : (
    <div className="home-feed-empty">
      <h3>{empty}</h3>
    </div>
  );
}

export default function HomeDiscovery() {
  const router = useRouter();
  const { identity, loading: identityLoading } = useIdentity();
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [activeId, setActiveId] = useState("");
  const [industriesError, setIndustriesError] = useState("");
  const [industriesLoading, setIndustriesLoading] = useState(true);
  const [industryAttempt, setIndustryAttempt] = useState(0);
  const [owned, setOwned] = useState<Industry[]>([]);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [question, setQuestion] = useState("");
  const [query, setQuery] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [recommended, setRecommended] = useState(false);
  const [limit, setLimit] = useState(6);
  const [browseLimit, setBrowseLimit] = useState(6);
  const searchField = useRef<HTMLInputElement>(null);
  const selected = industries.find((row) => row.id === activeId);
  const added = owned.some(
    (item) =>
      (item.id === activeId || item.source_industry_id === activeId) &&
      item.added,
  );

  useEffect(() => {
    let active = true;
    consumerApi<Industry[]>("community/industries")
      .then((items) => {
        if (!active) return;
        setIndustries(items);
        setActiveId(
          (id) =>
            items.find((item) => item.id === id)?.id ||
            items.find((item) => item.name === "人工智能")?.id ||
            items[0]?.id ||
            "",
        );
      })
      .catch((error: Error) => {
        if (active) setIndustriesError(error.message);
      })
      .finally(() => {
        if (active) setIndustriesLoading(false);
      });
    return () => {
      active = false;
    };
  }, [industryAttempt]);

  useEffect(() => {
    let active = true;
    if (identity)
      consumerApi<Industry[]>("account/me/community/industries")
        .then((items) => {
          if (active) setOwned(items);
        })
        .catch(() => {});
    else setOwned([]);
    return () => {
      active = false;
    };
  }, [identity?.user_id]);

  useEffect(() => {
    if (!new URLSearchParams(window.location.search).has("search")) return;
    searchField.current?.focus({ preventScroll: true });
    searchField.current?.scrollIntoView({ block: "center" });
  }, []);
  useEffect(() => {
    const timer = setTimeout(() => setSearchTerm(query.trim()), 220);
    return () => clearTimeout(timer);
  }, [query]);

  const feedEndpoint = identity
    ? "account/me/community/feed"
    : "community/reports";
  const industryFeed = useReportFeed(
    selected && !identityLoading
      ? `${feedEndpoint}?industry_id=${selected.id}&sort=newest&limit=4`
      : null,
  );
  const searchingReports = !!(query.trim() || searchTerm);
  const personalized = !!identity && recommended && !searchingReports;
  const browsingReports = searchingReports || personalized;
  const browseFeed = useReportFeed(
    !identityLoading && browsingReports && query.trim() === searchTerm
      ? `${feedEndpoint}?sort=${personalized ? "recommended" : "newest"}&limit=${browseLimit}&q=${encodeURIComponent(searchTerm)}`
      : null,
  );
  const standaloneFeed = useReportFeed(
    identityLoading ? null : `${feedEndpoint}?standalone=true&sort=newest&limit=24`,
  );
  const standaloneReports = standaloneFeed.reports.slice(0, limit);
  const hasStandaloneReports = standaloneReports.length > 0;
  useEffect(() => {
    if (hasStandaloneReports && window.location.hash === "#standalone-reports") {
      document.getElementById("standalone-reports")?.scrollIntoView();
    }
  }, [hasStandaloneReports]);

  async function toggleIndustry() {
    if (!selected || busy) return;
    if (!identity) {
      window.location.assign(loginHref(`/industries/${selected.id}`));
      return;
    }
    setBusy(true);
    setNotice("");
    try {
      const existing = owned.find(
        (row) =>
          row.id === selected.id || row.source_industry_id === selected.id,
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
      setOwned(
        await consumerApi<Industry[]>("account/me/community/industries"),
      );
      setNotice(
        added
          ? `已移除对「${selected.name}」的关注。`
          : `已将「${selected.name}」添加到我的行业。`,
      );
    } catch (error) {
      setNotice((error as Error).message);
    } finally {
      setBusy(false);
    }
  }

  function startChat(event: React.FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    const params = new URLSearchParams();
    if (selected) params.set("industry", selected.id);
    params.set("question", question.trim());
    router.push(`/chat?${params}`);
  }

  return (
    <div className="home-discovery">
      <section className="home-chat-hero" aria-labelledby="home-chat-title">
        <div className="home-chat-copy">
          <span className="home-chat-marker">行业与机遇预测 Agent</span>
          <h1 id="home-chat-title" aria-label="预测行业未来，发现下一次机遇。">
            <span>预测行业未来，</span>
            <span>发现下一次机遇。</span>
          </h1>
        </div>
        <form className="home-chat-form" onSubmit={startChat}>
          <div className="home-chat-input">
            <TextInput
              value={question}
              maxLength={1000}
              minLength={2}
              required
              aria-label="你想研究的问题"
              placeholder={
                selected
                  ? `聊聊你对${selected.name}行业的疑问…`
                  : "你想研究什么？"
              }
              onChange={(event) => setQuestion(event.target.value)}
            />
            <Button
              type="submit"
              aria-label="开始研究对话"
              disabled={!question.trim()}
            >
              开始研究 <PaperPlaneTilt size={17} aria-hidden="true" />
            </Button>
          </div>
        </form>
      </section>

      <div className="home-industry-grid">
        <section
          className="home-content-panel home-industries"
          aria-labelledby="home-industries-title"
        >
          <div className="home-panel-heading">
            <h2 id="home-industries-title">公开行业</h2>
            <Link href="/industries" className="text-action">
              全部行业 <ArrowUpRight size={15} aria-hidden="true" />
            </Link>
          </div>
          {industriesError ? (
            <div className="home-feed-empty">
              <p role="alert">{industriesError}</p>
              <Button
                className="secondary"
                onClick={() => {
                  setIndustriesError("");
                  setIndustriesLoading(true);
                  setIndustryAttempt((n) => n + 1);
                }}
              >
                重试
              </Button>
            </div>
          ) : selected ? (
            <IndustryBanner
              industries={industries}
              selectedId={selected.id}
              onSelect={(item) => {
                setActiveId(item.id);
                setNotice("");
              }}
              actions={
                <Button
                  className="home-industry-add"
                  disabled={busy || identityLoading}
                  onClick={toggleIndustry}
                >
                  {added ? <Check size={16} /> : <Plus size={16} />}
                  {busy
                    ? "正在保存…"
                    : added
                      ? "已添加到我的行业"
                      : "添加到我的行业"}
                </Button>
              }
            />
          ) : industriesLoading ? (
            <div
              className="skeleton home-industry-skeleton"
              aria-label="正在加载公开行业"
            />
          ) : (
            <div className="home-feed-empty">
              <h3>还没有公开行业</h3>
            </div>
          )}
          {notice && (
            <p className="inline-notice" role="status">
              {notice}
            </p>
          )}
        </section>

        <section
          id="public-reports"
          className="home-content-panel home-industry-reports"
          aria-labelledby="home-industry-reports-title"
        >
          <div className="home-panel-heading">
            <h2 id="home-industry-reports-title">
              {searchingReports
                ? "公开报告搜索"
                : personalized
                  ? "为你推荐的公开报告"
                  : "行业报告"}
            </h2>
            {selected && !browsingReports && (
              <Link
                href={`/industries/${selected.id}#public-reports`}
                className="text-action"
              >
                查看全部 <ArrowRight size={15} aria-hidden="true" />
              </Link>
            )}
          </div>
          <div className="home-report-tools">
            <label className="home-report-search">
              <MagnifyingGlass size={17} aria-hidden="true" />
              <TextInput
                ref={searchField}
                id="report-search"
                type="search"
                value={query}
                aria-label="搜索公开报告"
                placeholder="搜索公开报告"
                maxLength={100}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setBrowseLimit(6);
                }}
              />
            </label>
            {identity && (
              <Button
                className="quiet"
                disabled={!!query.trim()}
                onClick={() => {
                  setRecommended((value) => !value);
                  setBrowseLimit(6);
                }}
              >
                {recommended ? "返回行业报告" : "为你推荐"}
              </Button>
            )}
          </div>
          {browsingReports ? (
            <Feed
              feed={
                query.trim() !== searchTerm
                  ? { ...browseFeed, loading: true, error: "" }
                  : browseFeed
              }
              empty={
                personalized ? "还没有可推荐的公开报告" : "没有找到相关报告"
              }
            />
          ) : (
            <Feed
              feed={industryFeed}
              empty={selected ? "这个行业暂无公开报告" : "选择行业后即可浏览"}
              showIndustry={false}
            />
          )}
          {browsingReports &&
            query.trim() === searchTerm &&
            browseLimit < 24 &&
            browseFeed.reports.length === browseLimit && (
              <Button
                className="secondary home-load-more"
                onClick={() => setBrowseLimit((count) => count + 6)}
              >
                查看更多报告
              </Button>
            )}
        </section>
      </div>

      {hasStandaloneReports && (
        <section
          id="standalone-reports"
          className="home-content-panel home-standalone"
          aria-labelledby="home-standalone-title"
        >
          <div className="home-panel-heading">
            <h2 id="home-standalone-title">独立公开报告</h2>
          </div>
          <ReportList reports={standaloneReports} compact showIndustry={false} />
          {limit < standaloneFeed.reports.length && (
            <Button
              className="secondary home-load-more"
              onClick={() => setLimit((count) => count + 6)}
            >
              查看更多报告
            </Button>
          )}
        </section>
      )}
    </div>
  );
}
