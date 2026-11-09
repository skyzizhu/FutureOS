"use client";
import { useEffect, useState } from "react";
import type { CommunityActivityV1 } from "@futureos/contracts";
import Link from "next/link";
import { Heart, BookmarkSimple } from "@phosphor-icons/react";
import { Button } from "../ui/controls";
import { consumerApi, dateLabel } from "./api";
export default function SocialInbox() {
  const [items, setItems] = useState<CommunityActivityV1[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function load() {
    setError("");
    try {
      setItems(
        await consumerApi<CommunityActivityV1[]>(
          "account/me/community/notifications",
        ),
      );
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    void load();
  }, []);
  return (
    <section className="social-inbox">
      <div className="section-heading">
        <h2>互动消息</h2>
        <Button className="quiet" disabled={busy} onClick={load}>
          刷新互动消息
        </Button>
      </div>
      <p>读者点赞或收藏你的公开报告时，消息会保存在这里。</p>
      {!items.length && !error && <p>暂时没有新的互动。</p>}
      {items.map((item) => (
        <article key={item.id}>
          <h3>
            {item.kind === "like" ? (
              <Heart size={18} />
            ) : (
              <BookmarkSimple size={18} />
            )}{" "}
            {item.title}
          </h3>
          <p>{item.summary}</p>
          <time dateTime={item.created_at}>
            {dateLabel(item.created_at)} · {item.read ? "已读" : "未读"}
          </time>
          <div className="social-inbox-actions">
            <Link href={`/community/reports/${item.publication_id}`}>
              查看公开报告
            </Link>
            {!item.read && (
              <Button
                className="secondary"
                disabled={busy}
                onClick={async () => {
                  setBusy(true);
                  try {
                    await consumerApi(
                      `account/me/community/notifications/${item.id}/read`,
                      "POST",
                      {},
                    );
                    await load();
                    window.dispatchEvent(new Event("futureos:inbox-read"));
                  } catch (e) {
                    setError((e as Error).message);
                  } finally {
                    setBusy(false);
                  }
                }}
              >
                标记互动已读
              </Button>
            )}
          </div>
        </article>
      ))}
      {error && <p role="alert">{error}</p>}
    </section>
  );
}
