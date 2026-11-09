"use client";
import { Button, Select, Checkbox } from "../ui/controls";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ShareNetwork, Check, ArrowUpRight } from "@phosphor-icons/react";
import { consumerApi, type Industry, type PublicReport } from "./api";
type Preview = {
  title: string;
  summary: string;
  label: string;
  sections: { heading: string; text: string }[];
};
export default function ShareReport({
  reportId,
  versionId,
}: {
  reportId: string;
  versionId: string;
}) {
  const [industry, setIndustry] = useState("");
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [publication, setPublication] = useState<PublicReport | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    consumerApi<Industry[]>("community/industries")
      .then((rows) => {
        setIndustries(rows);
        setIndustry((current) => current || rows[0]?.id || "standalone");
      })
      .catch(() => setIndustry((current) => current || "standalone"));
  }, []);
  async function act(fn: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="share-panel">
      <div className="section-heading">
        <div>
          <h2>
            <ShareNetwork size={21} /> 公开一份行业观察
          </h2>
          <p>先预览，再决定。个人画像、私人建议和聊天记录不会随之公开。</p>
        </div>
        {!open && (
          <Button className="secondary" onClick={() => setOpen(true)}>
            公开报告
          </Button>
        )}
      </div>
      {open && (
        <>
          <label htmlFor="share-industry">公开位置</label>
          <Select
            id="share-industry"
            value={industry}
            onValueChange={(e) => {
              setIndustry(e);
              setPreview(null);
              setConfirmed(false);
              setPublication(null);
            }}
            disabled={busy}
          >
            <option value="" disabled>
              选择公开位置
            </option>
            <option value="standalone">独立公开 · 首页展示</option>
            {industries.map((i) => (
              <option key={i.id} value={i.id}>
                {i.name}
              </option>
            ))}
          </Select>
          <p>
            <Link href="/dashboard">
              需要公开自己的行业？先去个人中心公开行业。
            </Link>
          </p>
          <Button
            className="secondary"
            disabled={busy || !industry}
            onClick={() =>
              act(async () => {
                setPreview(
                  await consumerApi<Preview>(
                    `account/me/community/reports/${reportId}/preview`,
                    "POST",
                    {
                      industry_id: industry === "standalone" ? null : industry,
                      report_version_id: versionId,
                      confirm_public: true,
                    },
                  ),
                );
                setConfirmed(false);
                setPublication(null);
              })
            }
          >
            {busy ? "正在准备…" : "预览公开内容"}
          </Button>
          {preview && (
            <>
              <article className="share-preview">
                <span className="tag">
                  公开预览 ·{" "}
                  {preview.label === "DEMO" ? "演示研究" : "行业研究"}
                </span>
                <h3>{preview.title}</h3>
                <p>{preview.summary}</p>
                {preview.sections.map((s, i) => (
                  <div key={i}>
                    <h3>{s.heading}</h3>
                    <p>{s.text}</p>
                  </div>
                ))}
              </article>
              <label>
                <Checkbox
                  checked={confirmed}
                  onChange={(e) => setConfirmed(e.target.checked)}
                  disabled={busy || !!publication}
                />
                我已检查预览，愿意让其他人无需登录即可阅读以上内容。
              </label>
              <div className="form-actions">
                <Button
                  disabled={busy || !confirmed || !!publication}
                  onClick={() =>
                    act(async () => {
                      setPublication(
                        await consumerApi<PublicReport>(
                          `account/me/community/reports/${reportId}/publish`,
                          "POST",
                          {
                            industry_id:
                              industry === "standalone" ? null : industry,
                            report_version_id: versionId,
                            confirm_public: true,
                          },
                        ),
                      );
                      setNotice("报告已公开。你可以在个人中心随时撤回。");
                    })
                  }
                >
                  {publication ? (
                    <>
                      <Check size={17} /> 已公开
                    </>
                  ) : busy ? (
                    "正在发布…"
                  ) : (
                    "确认公开"
                  )}
                </Button>
                <Button
                  className="quiet"
                  onClick={() => {
                    setOpen(false);
                    setPreview(null);
                    setConfirmed(false);
                  }}
                >
                  收起
                </Button>
              </div>
            </>
          )}
          {publication && (
            <p>
              <Link
                className="text-action"
                href={`/community/reports/${publication.id}`}
              >
                查看公开报告 <ArrowUpRight size={15} />
              </Link>
            </p>
          )}
        </>
      )}
      {error && <p role="alert">{error}</p>}
      {notice && <p role="status">{notice}</p>}
    </section>
  );
}
