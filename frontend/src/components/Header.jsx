function Header() {
  return (
    <header className="header">
      <div className="container header-inner">

        <div className="logo">
          Voice2Minutes
        </div>

        <nav className="nav">
          <a href="#features">Features</a>
          <a href="#process">How it works</a>
          <a href="#preview">Preview</a>
        </nav>

        <button className="primary-btn">
          Start
        </button>

      </div>
    </header>
  );
}

export default Header;