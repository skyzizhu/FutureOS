"use client";
import {
  Children,
  Fragment,
  forwardRef,
  isValidElement,
  type ReactElement,
  type ReactNode,
  type InputHTMLAttributes,
  type TextareaHTMLAttributes,
  type ButtonHTMLAttributes,
  type SelectHTMLAttributes,
} from "react";
import * as Primitive from "@radix-ui/react-select";
import { CaretDown, CaretUp, Check } from "@phosphor-icons/react";
export const TextInput = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement>
>(function TextInput(props, ref) {
  return <input ref={ref} data-ui="input" {...props} />;
});
export const TextArea = forwardRef<
  HTMLTextAreaElement,
  TextareaHTMLAttributes<HTMLTextAreaElement>
>(function TextArea(props, ref) {
  return <textarea ref={ref} data-ui="textarea" {...props} />;
});
export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement>
>(function Button(props, ref) {
  return <button ref={ref} data-ui="button" {...props} />;
});
export const Checkbox = forwardRef<
  HTMLInputElement,
  Omit<InputHTMLAttributes<HTMLInputElement>, "type">
>(function Checkbox(props, ref) {
  return (
    <span className="ui-checkbox">
      <input ref={ref} type="checkbox" {...props} />
      <span className="ui-checkbox-mark" aria-hidden="true">
        <Check size={12} weight="bold" />
      </span>
    </span>
  );
});
export function Switch({
  label,
  hint,
  checked,
  onCheckedChange,
  disabled = false,
}: {
  label: string;
  hint?: string;
  checked: boolean;
  onCheckedChange: (value: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <label className="ui-switch-row">
      <span>
        <strong>{label}</strong>
        {hint && <small>{hint}</small>}
      </span>
      <span className="ui-switch">
        <input
          type="checkbox"
          role="switch"
          aria-label={label}
          checked={checked}
          disabled={disabled}
          onChange={(e) => onCheckedChange(e.target.checked)}
        />
        <span className="ui-switch-track" aria-hidden="true">
          <span />
        </span>
      </span>
    </label>
  );
}
type Item = {
  value: string;
  label: ReactNode;
  disabled?: boolean;
  group?: string;
};
function collect(children: ReactNode, group?: string): Item[] {
  const items: Item[] = [];
  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return;
    const node = child as ReactElement<{
      value?: string | number;
      children?: ReactNode;
      disabled?: boolean;
      label?: string;
    }>;
    if (node.type === Fragment)
      items.push(...collect(node.props.children, group));
    else if (node.type === "optgroup")
      items.push(...collect(node.props.children, node.props.label));
    else if (node.type === "option")
      items.push({
        value: String(node.props.value ?? node.props.children ?? ""),
        label: node.props.children,
        disabled: node.props.disabled,
        group,
      });
  });
  return items;
}
type Props = Omit<
  SelectHTMLAttributes<HTMLSelectElement>,
  "onChange" | "defaultValue" | "value" | "size" | "multiple"
> & {
  value?: string | number;
  onValueChange?: (value: string) => void;
  iconOnly?: ReactNode;
};
const empty = "__futureos_empty__";
export function Select({
  children,
  value = "",
  onValueChange,
  id,
  name,
  disabled,
  required,
  className,
  iconOnly,
  ...rest
}: Props) {
  const options = collect(children);
  let group: string | undefined;
  return (
    <Primitive.Root
      name={name}
      value={String(value) === "" ? empty : String(value)}
      onValueChange={(next) => {
        if (next) onValueChange?.(next === empty ? "" : next);
      }}
      disabled={disabled}
      required={required}
    >
      <Primitive.Trigger
        id={id}
        className={`ui-select-trigger ${iconOnly ? "ui-select-icon" : ""} ${className || ""}`}
        aria-label={rest["aria-label"]}
        aria-labelledby={rest["aria-labelledby"]}
        aria-describedby={rest["aria-describedby"]}
        aria-invalid={rest["aria-invalid"]}
        title={rest.title}
        data-ui="select"
        data-value={String(value)}
      >
        <span className={iconOnly ? "sr-only" : "ui-select-value"}>
          <Primitive.Value />
        </span>
        {iconOnly || (
          <Primitive.Icon>
            <CaretDown size={15} />
          </Primitive.Icon>
        )}
      </Primitive.Trigger>
      <Primitive.Portal>
        <Primitive.Content
          className="ui-select-popup"
          position="popper"
          sideOffset={7}
          collisionPadding={12}
          align="start"
        >
          <Primitive.ScrollUpButton className="ui-select-scroll">
            <CaretUp size={14} />
          </Primitive.ScrollUpButton>
          <Primitive.Viewport className="ui-select-viewport">
            {options.map((option, index) => {
              const heading = option.group !== group;
              group = option.group;
              return (
                <Fragment key={`${option.value}-${index}`}>
                  {heading && option.group && (
                    <div className="ui-select-group" role="presentation">
                      {option.group}
                    </div>
                  )}
                  <Primitive.Item
                    value={option.value === "" ? empty : option.value}
                    disabled={option.disabled}
                    className="ui-select-option"
                    data-value={option.value}
                  >
                    <Primitive.ItemText>{option.label}</Primitive.ItemText>
                    <Primitive.ItemIndicator>
                      <Check size={15} weight="bold" />
                    </Primitive.ItemIndicator>
                  </Primitive.Item>
                </Fragment>
              );
            })}
          </Primitive.Viewport>
          <Primitive.ScrollDownButton className="ui-select-scroll">
            <CaretDown size={14} />
          </Primitive.ScrollDownButton>
        </Primitive.Content>
      </Primitive.Portal>
    </Primitive.Root>
  );
}
