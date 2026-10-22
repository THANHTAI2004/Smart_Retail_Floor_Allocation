import { useState } from "react";

export function InputEditor({
  value,
  onSave,
  busy,
  template,
  label,
}: {
  value: unknown;
  onSave: (value: unknown) => Promise<void>;
  busy: boolean;
  template?: Record<string, unknown>;
  label: string;
}) {
  const [text, setText] = useState(JSON.stringify(value, null, 2));
  const [error, setError] = useState("");
  let parsed: Record<string, unknown> | null = null;
  try {
    const candidate = JSON.parse(text);
    if (!candidate || typeof candidate !== "object" || Array.isArray(candidate))
      throw new Error("Cần một đối tượng JSON");
    parsed = candidate;
  } catch {
    /* Display parse error on save, retain invalid draft. */
  }
  const items = parsed?.items;
  const rows = Array.isArray(items) ? (items as Record<string, unknown>[]) : [];
  const columns = [
    ...new Set(
      rows.flatMap((row) =>
        Object.keys(row).filter((key) =>
          ["string", "number", "boolean"].includes(typeof row[key]),
        ),
      ),
    ),
  ];
  const update = (value: unknown) => {
    setText(JSON.stringify(value, null, 2));
    setError("");
  };
  return (
    <div className="input-editor">
      {parsed && !Array.isArray(items) && (
        <div className="form-grid">
          {Object.entries(parsed)
            .filter(
              ([, value]) =>
                typeof value === "number" || typeof value === "string",
            )
            .map(([key, value]) => (
              <label key={key}>
                {key}
                <input
                  value={String(value)}
                  type={typeof value === "number" ? "number" : "text"}
                  step="any"
                  onChange={(e) =>
                    update({
                      ...parsed,
                      [key]:
                        typeof value === "number"
                          ? Number(e.target.value)
                          : e.target.value,
                    })
                  }
                />
              </label>
            ))}
        </div>
      )}
      {rows.length > 0 && (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                {columns.map((key) => (
                  <th key={key}>{key}</th>
                ))}
                <th>Xóa</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {columns.map((key) => (
                    <td key={key}>
                      {typeof row[key] === "boolean" ? (
                        <input
                          aria-label={`${key} dòng ${i + 1}`}
                          type="checkbox"
                          checked={Boolean(row[key])}
                          onChange={(e) =>
                            update({
                              ...parsed,
                              items: rows.map((r, j) =>
                                i === j ? { ...r, [key]: e.target.checked } : r,
                              ),
                            })
                          }
                        />
                      ) : (
                        <input
                          aria-label={`${key} dòng ${i + 1}`}
                          type={
                            typeof row[key] === "number" ? "number" : "text"
                          }
                          step="any"
                          value={String(row[key] ?? "")}
                          onChange={(e) =>
                            update({
                              ...parsed,
                              items: rows.map((r, j) =>
                                i === j
                                  ? {
                                      ...r,
                                      [key]:
                                        typeof row[key] === "number"
                                          ? Number(e.target.value)
                                          : e.target.value,
                                    }
                                  : r,
                              ),
                            })
                          }
                        />
                      )}
                    </td>
                  ))}
                  <td>
                    <button
                      aria-label={`Xóa dòng ${i + 1}`}
                      onClick={() =>
                        update({
                          ...parsed,
                          items: rows.filter((_, j) => i !== j),
                        })
                      }
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {template && (
        <button
          className="secondary"
          onClick={() =>
            update({
              ...parsed,
              items: [
                ...rows,
                {
                  ...template,
                  ...(template.id
                    ? { id: `${template.id}${rows.length + 1}` }
                    : {}),
                  ...(template.sku
                    ? { sku: `${template.sku}${rows.length + 1}` }
                    : {}),
                },
              ],
            })
          }
        >
          + Thêm dòng
        </button>
      )}
      <details open={!rows.length}>
        <summary>Dữ liệu JSON đầy đủ · cấu trúc lồng & nhập hàng loạt</summary>
        <label>
          {label}
          <textarea
            className="json-input"
            spellCheck={false}
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={16}
          />
        </label>
      </details>
      <div className="actions">
        <label className="file-button">
          Nhập JSON
          <input
            type="file"
            accept=".json,application/json"
            onChange={async (e) => {
              const file = e.target.files?.[0];
              if (file) {
                setText(await file.text());
                setError("");
              }
              e.target.value = "";
            }}
          />
        </label>
        <button
          className="primary"
          disabled={busy}
          onClick={async () => {
            try {
              const data = JSON.parse(text);
              setError("");
              await onSave(data);
            } catch (e) {
              setError(String(e));
            }
          }}
        >
          {busy ? "Đang lưu…" : "Lưu dữ liệu"}
        </button>
        <span className="muted">Kiểm tra cấu trúc và tham chiếu khi lưu</span>
      </div>
      {error && (
        <div className="notice error" role="alert">
          {error}
        </div>
      )}
    </div>
  );
}
