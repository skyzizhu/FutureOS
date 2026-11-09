"use client";
import { useEffect, useState } from "react";
import type { IndustryTrackingViewV1 } from "@futureos/contracts";
import { Switch } from "../ui/controls";
import { consumerApi } from "./api";
export default function Tracking({ industryId }: { industryId: string }) {
  const [data, setData] = useState<IndustryTrackingViewV1 | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setData(null);
    consumerApi<IndustryTrackingViewV1>(
      `account/me/community/industries/${industryId}/tracking`,
    )
      .then((value) => {
        if (active) setData(value);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [industryId]);
  async function change(
    key: "monitor_enabled" | "prediction_enabled" | "email_enabled",
    enabled: boolean,
  ) {
    if (!data || busy) return;
    const previous = data;
    setData({ ...data, [key]: enabled });
    setBusy(true);
    setError("");
    try {
      setData(
        await consumerApi<IndustryTrackingViewV1>(
          `account/me/community/industries/${industryId}/tracking`,
          "PUT",
          {
            monitor_enabled: data.monitor_enabled,
            prediction_enabled: data.prediction_enabled,
            email_enabled: data.email_enabled,
            [key]: enabled,
          },
        ),
      );
    } catch (e) {
      setData(previous);
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="industry-tracking">
      <h3>这个行业，按你的方式关注</h3>
      <p className="tracking-state">
        每个行业独立保存设置。
        {data?.status === "paused"
          ? "已暂停关注意愿。"
          : "实时执行等待抓取与提醒规则配置。"}
      </p>
      {data ? (
        <>
          <Switch
            label="行业动态监听"
            hint="记录关注意愿，规则配置后接入动态、行情与政策。"
            checked={data.monitor_enabled ?? true}
            disabled={busy}
            onCheckedChange={(value) => change("monitor_enabled", value)}
          />
          <Switch
            label="行业预测与建议"
            hint="关注行业未来及生活、工作、学习等维度的影响。"
            checked={data.prediction_enabled ?? true}
            disabled={busy}
            onCheckedChange={(value) => change("prediction_enabled", value)}
          />
          <Switch
            label="重要建议邮件提醒"
            hint="保存接收意愿；当前不会据此开始发送邮件。"
            checked={data.email_enabled ?? false}
            disabled={busy}
            onCheckedChange={(value) => change("email_enabled", value)}
          />
        </>
      ) : (
        <p className="tracking-state">正在读取设置…</p>
      )}
      {error && <p role="alert">{error}</p>}
    </div>
  );
}
