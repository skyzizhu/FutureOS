"use client";
import { TextInput, Button } from "../ui/controls";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  Plant,
  Plus,
  MagnifyingGlass,
} from "@phosphor-icons/react";
import { consumerApi, type Industry } from "./api";
export default function IndustryDirectory() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  async function load() {
    setError("");
    setLoading(true);
    try {
      setIndustries(await consumerApi<Industry[]>("community/industries"));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    void load();
  }, []);
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">探索你感兴趣的方向</p>
          <h1>每个行业，都有值得追问的未来。</h1>
          <p>看看大家正在关注什么，也为自己留一份观察清单。</p>
        </div>
        <Link className="button secondary" href="/dashboard?create=1">
          <Plus size={17} /> 创建我的行业
        </Link>
      </div>
      <div className="feed-search">
        <MagnifyingGlass size={18} />
        <TextInput
          type="search"
          placeholder="搜索行业"
          aria-label="搜索行业"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {error ? (
        <div className="empty-state">
          <p role="alert">{error}</p>
          <Button onClick={load}>重试</Button>
        </div>
      ) : loading ? (
        <div className="skeleton hero-skeleton" aria-label="正在加载行业" />
      ) : (
        <div className="industry-grid">
          {industries
            .filter((i) => `${i.name} ${i.description}`.includes(query))
            .map((industry) => (
              <Link
                className="industry-tile"
                key={industry.id}
                href={`/industries/${industry.id}`}
              >
                <Plant size={28} className="tile-icon" weight="duotone" />
                <h2>{industry.name}</h2>
                <p>{industry.description}</p>
                <div className="tile-footer">
                  <span>浏览公开报告</span>
                  <ArrowUpRight size={19} />
                </div>
              </Link>
            ))}
        </div>
      )}
      {!loading &&
        !error &&
        !industries.filter((i) => `${i.name} ${i.description}`.includes(query))
          .length && (
          <div className="empty-state">
            <h3>还没有这个行业</h3>
            <p>试试其他关键词，或创建自己的行业。</p>
            <Link href="/dashboard?create=1">创建行业</Link>
          </div>
        )}
    </>
  );
}
