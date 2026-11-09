"use client";
import { useEffect, useState, useRef } from "react";
import { Desktop, Moon, Sun } from "@phosphor-icons/react";
import { Select } from "../ui/controls";
import { useIdentity } from "./shell";
import { consumerApi } from "./api";
type Theme = "system" | "light" | "dark";
const valid = (value: string | null): Theme =>
  value === "light" || value === "dark" ? value : "system";
function apply(theme: Theme) {
  document.documentElement.dataset.theme =
    theme === "system"
      ? window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
      : theme;
  document.documentElement.dataset.themeMode = theme;
  try {
    localStorage.setItem("futureos_theme", theme);
  } catch {
    /* Browsers may disable local storage; the page still changes. */
  }
}

export function ThemeMenu() {
  const { identity } = useIdentity();
  const [theme, setTheme] = useState<Theme>("system");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const changed = useRef(false);
  useEffect(() => {
    const mode = valid(document.documentElement.dataset.themeMode || null);
    setTheme(mode);
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const sync = () => {
      if (document.documentElement.dataset.themeMode === "system")
        apply("system");
    };
    media.addEventListener("change", sync);
    const storage = (e: StorageEvent) => {
      if (e.key === "futureos_theme") {
        const next = valid(e.newValue);
        setTheme(next);
        apply(next);
      }
    };
    window.addEventListener("storage", storage);
    return () => {
      media.removeEventListener("change", sync);
      window.removeEventListener("storage", storage);
    };
  }, []);
  useEffect(() => {
    changed.current = false;
    let active = true;
    if (identity)
      consumerApi<{ theme: Theme }>("account/me/preferences")
        .then((p) => {
          if (active && !changed.current) {
            setTheme(p.theme);
            apply(p.theme);
          }
        })
        .catch(() => {});
    return () => {
      active = false;
    };
  }, [identity?.user_id]);
  async function choose(value: string) {
    const mode = valid(value);
    changed.current = true;
    setTheme(mode);
    apply(mode);
    setError("");
    if (identity) {
      setBusy(true);
      try {
        await consumerApi("account/me/preferences", "PUT", { theme: mode });
      } catch {
        setError("当前设备已切换，账号偏好保存失败，请重试。");
      } finally {
        setBusy(false);
      }
    }
  }
  return (
    <div className="theme-control">
      <Select
        aria-label="主题模式"
        title="外观设置"
        value={theme}
        onValueChange={choose}
        disabled={busy}
        iconOnly={
          theme === "dark" ? (
            <Moon size={18} aria-hidden="true" />
          ) : theme === "light" ? (
            <Sun size={18} aria-hidden="true" />
          ) : (
            <Desktop size={18} aria-hidden="true" />
          )
        }
      >
        <option value="system">跟随系统</option>
        <option value="light">浅色</option>
        <option value="dark">深色</option>
      </Select>
      {error && (
        <span className="theme-error" role="status">
          {error}
        </span>
      )}
    </div>
  );
}
