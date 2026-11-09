"use client";

import { CaretLeft, CaretRight } from "@phosphor-icons/react";
import { useEffect, useRef, type PointerEvent, type ReactNode } from "react";
import { Button } from "../ui/controls";
import type { Industry } from "./api";

const artwork: Record<string, string> = {
  technology: "industry-ai",
  energy: "industry-energy",
  healthcare: "industry-health",
  education: "report-learning",
  manufacturing: "report-code",
};

export function industryArtwork(domain: string) {
  const file = artwork[domain];
  return file ? `/images/${file}.webp` : undefined;
}

export default function IndustryBanner({
  industries,
  selectedId,
  onSelect,
  actions,
}: {
  industries: Industry[];
  selectedId: string;
  onSelect: (industry: Industry) => void;
  actions: ReactNode;
}) {
  const rail = useRef<HTMLDivElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const target = useRef<number | null>(null);
  const drag = useRef<{
    id: number;
    x: number;
    left: number;
    index: number;
    moved: boolean;
  } | null>(null);
  const index = Math.max(
    0,
    industries.findIndex((item) => item.id === selectedId),
  );

  function offset(slide: number) {
    const cards = rail.current?.children;
    const first = cards?.[0] as HTMLElement | undefined;
    const card = cards?.[slide] as HTMLElement | undefined;
    return first && card ? card.offsetLeft - first.offsetLeft : 0;
  }

  function nearest() {
    const viewport = rail.current;
    if (!viewport) return index;
    const { scrollLeft, scrollWidth, clientWidth } = viewport;
    if (scrollWidth - clientWidth - scrollLeft <= 2 && scrollLeft > 0) {
      return industries.length - 1;
    }
    let best = 0;
    let distance = Infinity;
    Array.from(viewport.children).forEach((card, i) => {
      const left =
        (card as HTMLElement).offsetLeft -
        (viewport.firstElementChild as HTMLElement).offsetLeft;
      const next = Math.abs(left - scrollLeft);
      if (next < distance) {
        distance = next;
        best = i;
      }
    });
    return best;
  }

  function settle() {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      if (drag.current?.moved) return;
      target.current = null;
      const current = industries[nearest()];
      if (current && current.id !== selectedId) onSelect(current);
    }, 140);
  }

  function goTo(slide: number) {
    const next = Math.max(0, Math.min(industries.length - 1, slide));
    target.current = next;
    rail.current?.scrollTo({
      left: offset(next),
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "instant"
        : "smooth",
    });
    settle();
  }

  function step(amount: number) {
    goTo((target.current ?? nearest()) + amount);
  }

  function startDrag(event: PointerEvent<HTMLDivElement>) {
    if (
      event.pointerType !== "mouse" ||
      event.button !== 0 ||
      (event.target instanceof Element && event.target.closest("button"))
    )
      return;
    drag.current = {
      id: event.pointerId,
      x: event.clientX,
      left: event.currentTarget.scrollLeft,
      index: nearest(),
      moved: false,
    };
  }

  function moveDrag(event: PointerEvent<HTMLDivElement>) {
    const gesture = drag.current;
    if (!gesture || gesture.id !== event.pointerId) return;
    const distance = event.clientX - gesture.x;
    if (!gesture.moved && Math.abs(distance) < 6) return;
    if (!gesture.moved) {
      gesture.moved = true;
      event.currentTarget.setPointerCapture(event.pointerId);
      event.currentTarget.dataset.dragging = "true";
      target.current = null;
    }
    event.currentTarget.scrollLeft = gesture.left - distance;
  }

  function finishDrag(event: PointerEvent<HTMLDivElement>) {
    const gesture = drag.current;
    drag.current = null;
    if (!gesture?.moved) return;
    const viewport = event.currentTarget;
    const distance = viewport.scrollLeft - gesture.left;
    let next = nearest();
    if (
      next === gesture.index &&
      Math.abs(distance) >= Math.min(110, viewport.clientWidth * 0.24)
    ) {
      next += Math.sign(distance);
    }
    delete viewport.dataset.dragging;
    goTo(next);
  }

  useEffect(() => {
    const viewport = rail.current;
    if (!viewport) return;
    const frame = requestAnimationFrame(() =>
      viewport.scrollTo({ left: offset(index), behavior: "instant" }),
    );
    return () => cancelAnimationFrame(frame);
  }, [industries]);

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current);
    },
    [],
  );

  return (
    <div
      className="industry-banner"
      role="region"
      aria-label="探索行业"
      aria-roledescription="轮播"
    >
      <span aria-live="polite" className="sr-only">
        {industries[index]?.name}，第 {index + 1} 个，共 {industries.length} 个
      </span>
      {industries.length > 1 && (
        <div className="industry-banner-controls">
          <Button
            type="button"
            className="industry-banner-arrow"
            aria-label="上一个行业"
            disabled={index === 0}
            onClick={() => step(-1)}
          >
            <CaretLeft size={16} aria-hidden="true" />
          </Button>
          <Button
            type="button"
            className="industry-banner-arrow"
            aria-label="下一个行业"
            disabled={index === industries.length - 1}
            onClick={() => step(1)}
          >
            <CaretRight size={16} aria-hidden="true" />
          </Button>
        </div>
      )}
      <div
        ref={rail}
        className="industry-banner-rail"
        role="group"
        tabIndex={0}
        aria-label="行业 Banner，可用方向键切换"
        onScroll={settle}
        onPointerDown={startDrag}
        onPointerMove={moveDrag}
        onPointerUp={finishDrag}
        onPointerCancel={finishDrag}
        onLostPointerCapture={finishDrag}
        onPointerLeave={() => {
          if (!drag.current?.moved) drag.current = null;
        }}
        onKeyDown={(event) => {
          if (event.target !== event.currentTarget) return;
          if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
            event.preventDefault();
            step(event.key === "ArrowLeft" ? -1 : 1);
          } else if (event.key === "Home" || event.key === "End") {
            event.preventDefault();
            goTo(event.key === "Home" ? 0 : industries.length - 1);
          }
        }}
      >
        {industries.map((industry, i) => {
          const image = industryArtwork(industry.domain);
          return (
            <div
              key={industry.id}
              className="industry-banner-slide"
              role="group"
              aria-roledescription="行业卡片"
              aria-label={`${i + 1} / ${industries.length}`}
              aria-hidden={industry.id !== selectedId}
              data-current={industry.id === selectedId}
            >
              {image && (
                <img
                  src={image}
                  alt=""
                  draggable={false}
                  loading={i === 0 ? "eager" : "lazy"}
                  fetchPriority={i === 0 ? "high" : "auto"}
                />
              )}
              <div className="industry-banner-copy">
                <h2>{industry.name}</h2>
                <p>{industry.description}</p>
                {industry.id === selectedId && actions}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
