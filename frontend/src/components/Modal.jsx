// Generic modal dialog: a full-screen backdrop with a centred panel, used by the
// authoring forms. Clicking the backdrop closes the modal; clicking inside the
// panel does not — the panel stops the click event bubbling up to the backdrop's
// onClose handler, so an editor can't lose their work by clicking the form.
export default function Modal({ title, children, onClose }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        {title && <h2>{title}</h2>}
        {children}
      </div>
    </div>
  );
}
