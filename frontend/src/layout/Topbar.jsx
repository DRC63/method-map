export default function Topbar({ title }) {
  return (
    <header className="topbar">
      <h1>{title}</h1>
      <span className="topbar-brand">P3M<span className="brand-ai">AI</span></span>
    </header>
  );
}
