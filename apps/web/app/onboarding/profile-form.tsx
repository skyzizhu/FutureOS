"use client";
import { Button, Select, TextInput, Checkbox } from "../components/ui/controls";

import { useEffect, useState } from "react";
import type {
  ProfileInputV1,
  ProfileViewV1,
  CountryCatalogV1,
} from "@futureos/contracts";
import { Plus, X, ArrowRight } from "@phosphor-icons/react";
import { safeReturnPath } from "../components/consumer/api";
import { accountApi } from "../components/account-api";
type Entry = {
  code: string;
  parent_code: string | null;
  label: string;
  level: number;
};
const commonGoals = [
  "了解行业趋势",
  "寻找职业机会",
  "学习或转行",
  "探索创业方向",
  "改善产品或业务",
  "观察市场机遇",
];
const commonCountries = [
  "CN",
  "US",
  "GB",
  "CA",
  "AU",
  "SG",
  "JP",
  "KR",
  "DE",
  "FR",
];
export default function ProfileForm() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [countries, setCountries] = useState<CountryCatalogV1["entries"]>([]);
  const [parent, setParent] = useState("");
  const [child, setChild] = useState("");
  const [detail, setDetail] = useState("");
  const [occupation, setOccupation] = useState("");
  const [country, setCountry] = useState("");
  const [subdivision, setSubdivision] = useState("");
  const [legacyRegion, setLegacyRegion] = useState("");
  const [gender, setGender] = useState("");
  const [age, setAge] = useState("");
  const [goals, setGoals] = useState<string[]>([]);
  const [goalDraft, setGoalDraft] = useState("");
  const [tasks, setTasks] = useState<string[]>([]);
  const [taskDraft, setTaskDraft] = useState("");
  const [minutes, setMinutes] = useState("");
  const [optional, setOptional] = useState(false);
  const [experiment, setExperiment] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [catalogError, setCatalogError] = useState("");
  const [ready, setReady] = useState(false);
  async function load() {
    setCatalogError("");
    setReady(false);
    try {
      const catalog = await accountApi("taxonomies/industries");
      setEntries(catalog.entries);
    } catch {
      setCatalogError("行业目录暂时无法加载，请重试。");
    }
    try {
      const catalog: CountryCatalogV1 = await accountApi(
        "taxonomies/countries",
      );
      setCountries(catalog.entries);
    } catch {
      setCatalogError("国家／地区目录暂时无法加载，请重试；行业仍可单独填写。");
    }
    try {
      const data: ProfileViewV1 = await accountApi("me/profile");
      const p = data.profile;
      setParent(p.industry_l1_code);
      setChild(p.industry_l2_code);
      setDetail(p.industry_detail || "");
      setOccupation(p.occupation_text || "");
      setCountry(p.country_code || "");
      setSubdivision(p.subdivision || "");
      setLegacyRegion(p.country_code ? "" : p.region || "");
      setGender(p.gender || "");
      setAge(p.age == null ? "" : String(p.age));
      setGoals(p.goals || []);
      setTasks(p.tasks || []);
      setMinutes(
        p.available_minutes_per_week == null
          ? ""
          : String(p.available_minutes_per_week),
      );
      setOptional(p.use_optional_fields === true);
      setExperiment(p.allow_low_cost_experiments === true);
      setReady(true);
    } catch (e) {
      if ((e as Error).message.includes("PROFILE_REQUIRED")) setReady(true);
      else setError("个人资料尚未读取成功，请重试后再保存，避免覆盖已有资料。");
    }
  }
  useEffect(() => {
    void load();
  }, []);
  function focus(id: string) {
    document.getElementById(id)?.focus();
  }
  function addGoal() {
    const value = goalDraft.trim();
    if (!value || goals.length >= 5) return;
    if (!goals.includes(value)) setGoals([...goals, value]);
    setGoalDraft("");
  }
  function addTask() {
    const value = taskDraft.trim();
    if (!value || tasks.length >= 8) return;
    if (!tasks.includes(value)) setTasks([...tasks, value]);
    setTaskDraft("");
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (busy || !ready) return;
    setError("");
    if (!parent || !child) {
      setError("请先选择一级行业和对应的二级行业。");
      focus(!parent ? "industry-parent" : "industry-child");
      return;
    }
    if (child.endsWith("_other") && !detail.trim()) {
      setError("请简单填写你的细分行业。");
      focus("industry-detail");
      return;
    }
    if (subdivision.trim() && !country) {
      setError("请先选择国家／地区，再填写省或州。");
      focus("profile-country");
      return;
    }
    if (
      age !== "" &&
      (!Number.isInteger(Number(age)) || Number(age) < 1 || Number(age) > 120)
    ) {
      setError("年龄请填写1–120之间的整数，也可以留空。");
      focus("profile-age");
      return;
    }
    if (
      (goalDraft.trim() &&
        !goals.includes(goalDraft.trim()) &&
        goals.length >= 5) ||
      (taskDraft.trim() &&
        !tasks.includes(taskDraft.trim()) &&
        tasks.length >= 8)
    ) {
      setError("关注方向最多5项，工作内容最多8项；请先移除不需要的条目。");
      return;
    }
    setBusy(true);
    try {
      const nextGoals =
        goalDraft.trim() && !goals.includes(goalDraft.trim())
          ? [...goals, goalDraft.trim()]
          : goals;
      const nextTasks =
        taskDraft.trim() && !tasks.includes(taskDraft.trim())
          ? [...tasks, taskDraft.trim()]
          : tasks;
      const profile: ProfileInputV1 = {
        industry_l1_code: parent,
        industry_l2_code: child,
        industry_detail: child.endsWith("_other") ? detail.trim() : "",
        occupation_text: occupation.trim(),
        country_code: country,
        subdivision: subdivision.trim(),
        region: country || legacyRegion,
        gender: gender ? (gender as ProfileInputV1["gender"]) : null,
        age: age === "" ? null : Number(age),
        goals: nextGoals as ProfileInputV1["goals"],
        tasks: nextTasks as ProfileInputV1["tasks"],
        available_minutes_per_week: minutes === "" ? null : Number(minutes),
        allow_low_cost_experiments: experiment,
        use_optional_fields: optional,
        locale: "zh-CN",
        timezone: "Asia/Shanghai",
      };
      await accountApi("me/profile", "PUT", profile);
      const next =
        new URLSearchParams(window.location.search).get("next") || "";
      window.location.assign(safeReturnPath(next));
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败，请重试。");
    } finally {
      setBusy(false);
    }
  }
  const goalChoices = [
    ...commonGoals,
    ...goals.filter((g) => !commonGoals.includes(g)),
  ];
  const subdivisionLabel =
    country === "US"
      ? "州（选填）"
      : country === "CN"
        ? "省／自治区／直辖市（选填）"
        : country === "CA"
          ? "省／地区（选填）"
          : "省／州／地区（选填）";
  return (
    <section className="profile-card">
      <h2>让报告更贴近你关心的变化</h2>
      <p className="profile-intro">
        先选大方向，再选具体行业。其余资料都可以跳过，之后随时修改。
      </p>
      {catalogError && (
        <div className="inline-notice">
          <p role="alert">{catalogError}</p>
          <Button type="button" className="quiet" onClick={load}>
            重新加载资料选项
          </Button>
        </div>
      )}
      <form onSubmit={submit} noValidate>
        <div className="profile-grid">
          <div>
            <label htmlFor="industry-parent">一级行业（必选）</label>
            <Select
              id="industry-parent"
              required
              value={parent}
              disabled={busy || !ready}
              onValueChange={(e) => {
                setParent(e);
                setChild("");
                setDetail("");
              }}
            >
              <option value="">选择行业大方向</option>
              {entries
                .filter((e) => e.level === 1)
                .map((e) => (
                  <option key={e.code} value={e.code}>
                    {e.label}
                  </option>
                ))}
            </Select>
          </div>
          <div>
            <label htmlFor="industry-child">二级行业（必选）</label>
            <Select
              id="industry-child"
              required
              value={child}
              onValueChange={(e) => {
                setChild(e);
                setDetail("");
              }}
              disabled={!parent || busy || !ready}
            >
              <option value="">
                {parent ? "选择具体细分方向" : "先选择一级行业"}
              </option>
              {entries
                .filter((e) => e.parent_code === parent)
                .map((e) => (
                  <option key={e.code} value={e.code}>
                    {e.label}
                  </option>
                ))}
            </Select>
          </div>
        </div>
        {parent === "not_applicable" && (
          <p className="profile-help">
            这是身份兜底选项，适合在校学生、退休或暂不按职业填写的人。你仍然可以添加并研究自己感兴趣的行业。
          </p>
        )}
        {child.endsWith("_other") && (
          <div className="profile-field">
            <label htmlFor="industry-detail">你的细分行业</label>
            <TextInput
              id="industry-detail"
              value={detail}
              maxLength={120}
              placeholder="例如：低空飞行器运营、AI 辅助珠宝设计"
              onChange={(e) => setDetail(e.target.value)}
              required
            />
          </div>
        )}
        <p className="profile-help">
          没有找到合适的细分？选择该行业下的“其他细分方向”，填写自己的方向。
        </p>
        <details className="profile-optional">
          <summary>
            个性化资料（选填）<span>补充你的位置、职业和关注点</span>
          </summary>
          <div className="profile-field">
            <label htmlFor="occupation">岗位或工作内容</label>
            <TextInput
              id="occupation"
              maxLength={300}
              value={occupation}
              onChange={(e) => setOccupation(e.target.value)}
              placeholder="例如：软件工程师、餐饮店主、在校学生"
            />
            <p className="profile-help">
              帮助理解变化与你的工作有什么关系，不填也可以获取行业报告。
            </p>
          </div>
          <div className="profile-grid">
            <div>
              <label htmlFor="profile-country">国家／地区（选填）</label>
              <Select
                id="profile-country"
                value={country}
                onValueChange={(e) => {
                  setCountry(e);
                  setSubdivision("");
                }}
                disabled={!countries.length}
              >
                <option value="">不填写</option>
                <optgroup label="常用国家／地区">
                  {commonCountries
                    .map((code) => countries.find((c) => c.code === code))
                    .filter((c) => !!c)
                    .map((c) => (
                      <option key={c.code} value={c.code}>
                        {c.label}
                      </option>
                    ))}
                </optgroup>
                <optgroup label="其他国家／地区">
                  {countries
                    .filter((c) => !commonCountries.includes(c.code))
                    .sort((a, b) => a.label.localeCompare(b.label, "zh-CN"))
                    .map((c) => (
                      <option key={c.code} value={c.code}>
                        {c.label}
                      </option>
                    ))}
                </optgroup>
              </Select>
            </div>
            <div>
              <label htmlFor="profile-subdivision">{subdivisionLabel}</label>
              <TextInput
                id="profile-subdivision"
                value={subdivision}
                maxLength={100}
                onChange={(e) => setSubdivision(e.target.value)}
                placeholder={
                  country === "US"
                    ? "例如：California 或加利福尼亚州"
                    : country === "CN"
                      ? "例如：浙江省、上海市"
                      : "直接填写，无需从列表选择"
                }
              />
            </div>
          </div>
          {legacyRegion && (
            <p className="profile-help">
              原地区信息：{legacyRegion}
              。选择国家后可按新的方式保存；暂不调整时会保留。
            </p>
          )}
          <div className="profile-grid">
            <div>
              <label htmlFor="profile-gender">性别（选填）</label>
              <Select
                id="profile-gender"
                value={gender}
                onValueChange={(e) => setGender(e)}
              >
                <option value="">不填写</option>
                <option value="female">女</option>
                <option value="male">男</option>
                <option value="other">其他</option>
              </Select>
            </div>
            <div>
              <label htmlFor="profile-age">年龄（选填）</label>
              <TextInput
                id="profile-age"
                type="number"
                inputMode="numeric"
                min={1}
                max={120}
                step={1}
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="例如：28"
              />
            </div>
          </div>
          <p className="profile-help">
            年龄和性别仅补充个人资料，目前不参与行业预测或推荐排序。
          </p>
          <fieldset className="profile-goals">
            <legend>你更关心什么？（选填）</legend>
            <p className="profile-help">
              用于突出报告中与你有关的内容。可多选，最多5项。
            </p>
            <div className="profile-choice-list">
              {goalChoices.map((goal) => (
                <label
                  key={goal}
                  className={goals.includes(goal) ? "chosen" : ""}
                >
                  <Checkbox
                    checked={goals.includes(goal)}
                    disabled={!goals.includes(goal) && goals.length >= 5}
                    onChange={(e) =>
                      setGoals(
                        e.target.checked
                          ? [...goals, goal]
                          : goals.filter((g) => g !== goal),
                      )
                    }
                  />
                  {goal}
                </label>
              ))}
            </div>
            <div className="profile-inline-add">
              <TextInput
                aria-label="补充关注方向"
                value={goalDraft}
                maxLength={200}
                onChange={(e) => setGoalDraft(e.target.value)}
                placeholder="也可以说说自己关心的方向"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.nativeEvent.isComposing) {
                    e.preventDefault();
                    addGoal();
                  }
                }}
              />
              <Button
                className="secondary"
                type="button"
                disabled={!goalDraft.trim() || goals.length >= 5}
                onClick={addGoal}
              >
                <Plus size={16} /> 添加
              </Button>
            </div>
          </fieldset>
          <details className="profile-advanced">
            <summary>进阶：定制行动建议（可跳过）</summary>
            <p className="profile-help">
              如果你希望报告进一步讨论“我可以怎么做”，再填写下面的内容。
            </p>
            <label htmlFor="profile-task">你希望重点关注的工作／业务</label>
            <p className="profile-help">
              例如写代码、经营门店、制作内容。帮助判断哪些变化可能影响你的日常，不是在这里安排任务。
            </p>
            <div className="profile-inline-add">
              <TextInput
                id="profile-task"
                maxLength={200}
                value={taskDraft}
                onChange={(e) => setTaskDraft(e.target.value)}
                placeholder="填写一项工作内容"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.nativeEvent.isComposing) {
                    e.preventDefault();
                    addTask();
                  }
                }}
              />
              <Button
                type="button"
                className="secondary"
                onClick={addTask}
                disabled={!taskDraft.trim() || tasks.length >= 8}
              >
                添加工作内容
              </Button>
            </div>
            <div className="profile-task-list">
              {tasks.map((task) => (
                <span key={task}>
                  {task}
                  <Button
                    type="button"
                    className="icon-button"
                    aria-label={`移除工作内容：${task}`}
                    onClick={() => setTasks(tasks.filter((t) => t !== task))}
                  >
                    <X size={13} />
                  </Button>
                </span>
              ))}
            </div>
            <p className="profile-help">
              最多8项，逐项添加即可；未点击添加的文字也会随保存一并保存。
            </p>
            <label htmlFor="time-budget">每周愿意花多久尝试新方法？</label>
            <Select
              id="time-budget"
              value={minutes}
              onValueChange={(e) => setMinutes(e)}
            >
              <option value="">不设置</option>
              <option value="0">暂不考虑尝试</option>
              <option value="15">15分钟</option>
              <option value="30">30分钟</option>
              <option value="60">1小时</option>
              <option value="120">2小时</option>
              {minutes && !["0", "15", "30", "60", "120"].includes(minutes) && (
                <option value={minutes}>{minutes}分钟（已保存）</option>
              )}
            </Select>
            <p className="profile-help">
              只用于约束建议的投入时间，不影响报告生成速度，也不是要求你每周必须完成任务。
            </p>
            <label className="profile-consent">
              <Checkbox
                checked={experiment}
                onChange={(e) => setExperiment(e.target.checked)}
              />
              如果适合我，可以推荐可随时停止、无需新增付费的小尝试
            </label>
          </details>
          <label className="profile-consent">
            <Checkbox
              checked={optional}
              onChange={(e) => setOptional(e.target.checked)}
            />
            允许报告使用岗位、地区和关注偏好
          </label>
          <p className="profile-help">
            不勾选时，选填内容只保存在你的个人资料中，报告仅使用行业。年龄和性别不进入研究快照。
          </p>
        </details>
        {error && (
          <div className="auth-feedback auth-error" role="alert">
            {error}
            {!ready && (
              <Button className="quiet" type="button" onClick={load}>
                重新读取个人资料
              </Button>
            )}
          </div>
        )}
        <div className="profile-save">
          <p>修改仅影响之后生成的报告，已完成报告保留原来的版本。</p>
          <Button type="submit" disabled={busy || !ready || !parent || !child}>
            {busy ? "正在保存…" : "保存画像"}
            <ArrowRight size={16} />
          </Button>
        </div>
      </form>
    </section>
  );
}
