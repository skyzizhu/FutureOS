"use client";
import Link from "next/link";
import { useEffect, useState, useRef } from "react";
import {
  ArrowLeft,
  BookmarkSimple,
  ChatCircleDots,
  ArrowRight,
  Heart,
  DownloadSimple,
  Eye,
} from "@phosphor-icons/react";
import { Button, Select } from "../ui/controls";
import {
  consumerApi,
  dateLabel,
  loginHref,
  type Industry,
  type PublicReport,
} from "./api";
import { useIdentity } from "./shell";
export default function PublicReader({ id }: { id: string }) {
  const { identity, loading: identityLoading } = useIdentity();
  const [report, setReport] = useState<PublicReport | null>(null);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [folder, setFolder] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [metaLoading, setMetaLoading] = useState(false);
  useEffect(() => {
    let active = true;
    setError("");
    consumerApi<PublicReport>(`community/reports/${id}`)
      .then((value) => {
        if (active) {
          setReport((current) => ({
            ...value,
            views_count: Math.max(
              current?.id === value.id ? (current.views_count ?? 0) : 0,
              value.views_count ?? 0,
            ),
          }));
          setFolder((current) => current || value.industry_id || "");
        }
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [id]);
  useEffect(() => {
    let active = true;
    if (!identity) return;
    setMetaLoading(true);
    Promise.all([
      consumerApi<Industry[]>("account/me/community/industries"),
      consumerApi<PublicReport>(`account/me/community/reports/${id}`),
    ])
      .then(([rows, value]) => {
        if (active) {
          setIndustries(rows);
          setReport((current) => ({
            ...value,
            views_count: Math.max(
              current?.id === value.id ? (current.views_count ?? 0) : 0,
              value.views_count ?? 0,
            ),
          }));
          setFolder(
            value.saved_industry_id ||
              rows.find((i) => i.source_industry_id === value.industry_id)
                ?.id ||
              value.industry_id ||
              rows[0]?.id ||
              "",
          );
        }
      })
      .catch((e) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setMetaLoading(false);
      });
    return () => {
      active = false;
    };
  }, [id, identity?.user_id]);
  const counted = useRef(new Set<string>());
  useEffect(() => {
    if (!report?.id) return;
    const record = () => {
      if (document.visibilityState !== "visible" || counted.current.has(id))
        return;
      counted.current.add(id);
      consumerApi<PublicReport>(`community/reports/${id}/read`, "POST", {})
        .then((value) =>
          setReport((current) =>
            current?.id === id
              ? {
                  ...current,
                  views_count: Math.max(
                    current.views_count ?? 0,
                    value.views_count ?? 0,
                  ),
                }
              : current,
          ),
        )
        .catch(() => {});
    };
    record();
    document.addEventListener("visibilitychange", record);
    return () => document.removeEventListener("visibilitychange", record);
  }, [id, report?.id]);
  function requireLogin() {
    if (identity) return true;
    window.location.assign(loginHref(`/community/reports/${id}`));
    return false;
  }
  async function act(fn: () => Promise<void>) {
    if (!requireLogin() || busy) return;
    setBusy(true);
    setError("");
    try {
      await fn();
      setReport(
        await consumerApi<PublicReport>(`account/me/community/reports/${id}`),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function save() {
    if (!report) return;
    await act(async () => {
      let target = folder;
      if (!report.saved && !industries.find((i) => i.id === folder)?.owned) {
        const own = await consumerApi<Industry>(
          `account/me/community/industries/${folder}/add`,
          "PUT",
        );
        target = own.id;
        setFolder(target);
        setIndustries((current) => [
          ...current.filter((i) => i.id !== own.id),
          own,
        ]);
      }
      await consumerApi(
        `account/me/community/reports/${id}/bookmark`,
        report.saved ? "DELETE" : "PUT",
        report.saved ? undefined : { industry_id: target },
      );
      setNotice(
        report.saved
          ? "已取消收藏。"
          : report.sample
            ? "已收藏到自己的行业。"
            : "已收藏到自己的行业，作者将收到站内通知。",
      );
    });
  }
  async function download() {
    if (!requireLogin() || busy) return;
    setBusy(true);
    setError("");
    try {
      const response = await fetch(
        `/api/account/me/community/reports/${id}/download`,
        { cache: "no-store" },
      );
      if (!response.ok) {
        const failure = await response.json();
        throw new Error(failure.message || "下载失败，请重新登录后重试。");
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `futureos-report-${id}.md`;
      anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice("已准备公开报告文件。");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (error && !report)
    return (
      <div className="empty-state">
        <h1>这份报告暂时无法查看</h1>
        <p role="alert">{error}</p>
        <Link href="/">返回发现</Link>
      </div>
    );
  if (!report)
    return <div className="skeleton hero-skeleton" aria-label="正在加载报告" />;
  const folders =
    industries.some(
      (i) =>
        i.id === report.industry_id ||
        (i.source_industry_id === report.industry_id &&
          folder !== report.industry_id),
    ) || !report.industry_id
      ? industries
      : [
          {
            id: report.industry_id,
            name: report.industry_name + " · 公开来源",
          },
          ...industries,
        ];
  const disabled = busy || identityLoading || metaLoading;
  return (
    <div className="reading-page">
      <Link
        className="back-link"
        href={
          report.industry_id
            ? `/industries/${report.industry_id}`
            : "/#standalone-reports"
        }
      >
        <ArrowLeft size={16} />{" "}
        {report.industry_id
          ? report.industry_name + " · 公开报告"
          : "返回独立公开报告"}
      </Link>
      <div>
        <span className="tag">
          {report.sample
            ? "阅读示例"
            : report.label === "DEMO"
              ? "演示资料 · 公开报告"
              : "公开报告"}
        </span>
      </div>
      <h1 className="reading-title">{report.title}</h1>
      <p className="reading-deck">{report.summary}</p>
      <div className="reading-byline">
        <span>{report.author}</span>
        <span>{dateLabel(report.created_at)}</span>
        {report.industry_id && (
          <Link href={`/industries/${report.industry_id}`}>
            {report.industry_name} <ArrowRight size={12} />
          </Link>
        )}
      </div>
      <div className="social-counts">
        <span>
          <Eye size={15} /> {report.views_count ?? 0} 次阅读
        </span>
        <span>
          <Heart size={15} /> {report.likes_count} 人点赞
        </span>
        <span>
          <BookmarkSimple size={15} /> {report.bookmarks_count} 人收藏
        </span>
      </div>
      <img
        className="reading-cover"
        src={`/images/${report.image.replace(/\.png$/, ".webp")}`}
        alt="行业研究配图"
      />
      <div className="reading-content">
        {report.sections.map((section, index) => (
          <section key={index}>
            <h2>{section.heading}</h2>
            <p>{section.text}</p>
          </section>
        ))}
      </div>
      <p className="inline-notice">
        {report.sample
          ? "示例用于体验产品，不是实际执行的研究，也不构成现实预测或行动建议。"
          : report.label === "DEMO"
            ? "本报告使用演示资料，不作为现实建议。公开内容不含作者的个人画像和私人建议。"
            : "预测具有不确定性。公开内容固定于发布时的版本，不会随作者私人报告自动更新。"}
      </p>
      {notice && <p role="status">{notice}</p>}
      {error && <p role="alert">{error}</p>}
      <div className="reading-toolbar">
        <div>
          <label>
            <span className="sr-only">收藏到哪个行业</span>
            <Select
              aria-label="收藏到哪个行业"
              value={folder}
              onValueChange={setFolder}
              disabled={report.saved || disabled}
            >
              {!folder && <option value="">选择收藏行业</option>}
              {folders.map((i) => (
                <option value={i.id} key={i.id}>
                  {i.name}
                </option>
              ))}
            </Select>
          </label>
          {identity && !folders.length && (
            <p>
              <Link href="/dashboard?create=1">添加一个行业后即可收藏报告</Link>
            </p>
          )}
          <div className="public-report-actions">
            <Button
              className="social-action"
              aria-pressed={report.liked}
              aria-label={report.liked ? "已点赞" : "点赞报告"}
              disabled={disabled}
              onClick={() =>
                act(async () => {
                  await consumerApi(
                    `account/me/community/reports/${id}/like`,
                    report.liked ? "DELETE" : "PUT",
                  );
                  setNotice(
                    report.liked
                      ? "已取消点赞。"
                      : report.sample
                        ? "点赞已保存。"
                        : "点赞已保存，作者将收到站内通知。",
                  );
                })
              }
            >
              <Heart size={17} weight={report.liked ? "fill" : "regular"} />
              {report.liked ? "已点赞" : "点赞"}
            </Button>
            <Button
              className="social-action"
              aria-pressed={report.saved}
              disabled={disabled || (!!identity && !report.saved && !folder)}
              onClick={save}
            >
              <BookmarkSimple
                size={17}
                weight={report.saved ? "fill" : "regular"}
              />
              {report.saved ? "已收藏" : "收藏报告"}
            </Button>
            <Button
              className="social-action"
              disabled={disabled}
              onClick={download}
            >
              <DownloadSimple size={17} /> 下载报告
            </Button>
          </div>
        </div>
        <Link
          className="button"
          href={
            report.industry_id
              ? `/chat?industry=${report.industry_id}&question=${encodeURIComponent(`我想继续了解${report.industry_name}行业的变化`)}`
              : `/chat?question=${encodeURIComponent(`我想继续研究这份公开报告的主题：${report.title}`)}`
          }
        >
          <ChatCircleDots size={17} />{" "}
          {report.industry_id ? "研究这个行业" : "继续研究这个主题"}
        </Link>
      </div>
    </div>
  );
}
