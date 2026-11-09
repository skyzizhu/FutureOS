"use client";
import Link from "next/link";
import {
  ArrowUpRight,
  BookmarkSimple,
  FileText,
  Eye,
} from "@phosphor-icons/react";
import type { PublicReport } from "./api";
export default function ReportList({
  reports,
  compact = false,
  showIndustry = true,
}: {
  reports: PublicReport[];
  compact?: boolean;
  showIndustry?: boolean;
}) {
  return (
    <div
      className={compact ? "report-feed report-feed-compact" : "report-feed"}
    >
      {reports.map((report) => (
        <Link
          className="report-row"
          href={`/community/reports/${report.id}`}
          key={report.id}
        >
          {!compact && (
            <div className="report-avatar">
              <FileText size={20} weight="duotone" />
            </div>
          )}
          <div className="report-row-body">
            {!compact && <span className="tag">{report.industry_name}</span>}
            <h3>{report.title}</h3>
            <p>{report.summary}</p>
            <div className="report-meta">
              {compact && showIndustry && <span>{report.industry_name}</span>}
              {(!compact || !report.sample) && <span>{report.author}</span>}
              {(!compact || report.sample || report.label === "DEMO") && (
                <span>
                  {compact
                    ? report.sample ? "阅读示例" : "演示报告"
                    : report.sample
                      ? "示例公开报告"
                      : report.label === "DEMO"
                        ? "演示研究 · 公开报告"
                        : "公开报告"}
                </span>
              )}
              <span className="report-counts">
                <span>
                  <Eye size={13} aria-hidden="true" />{" "}
                  {report.views_count ?? 0} 次阅读
                </span>
                <span>
                  <BookmarkSimple size={13} aria-hidden="true" />{" "}
                  {report.bookmarks_count ?? 0} 人收藏
                </span>
              </span>
              {report.saved && (
                <span>
                  <BookmarkSimple size={13} weight="fill" aria-hidden="true" />
                  已收藏
                </span>
              )}
              {report.reason && (
                <span className="recommendation-reason">{report.reason}</span>
              )}
            </div>
          </div>
          {!compact && (
            <div className="report-cover">
              <img
                src={`/images/${report.image.replace(/\.png$/, ".webp")}`}
                alt=""
                loading="lazy"
              />
            </div>
          )}
          <ArrowUpRight className="report-hover-arrow" size={22} />
        </Link>
      ))}
    </div>
  );
}
