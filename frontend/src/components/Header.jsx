function Header({ onLogoClick }) {
  const handleLogoClick = (event) => {
    event.preventDefault();
    onLogoClick();
  };

  return (
    <header className="header">
      <div className="container header-inner">
        <a
          href="/"
          className="logo"
          onClick={handleLogoClick}
        >
          Voice2Minutes
        </a>

        <nav className="nav">
          <a href="#features">Features</a>
          <a href="#process">How it works</a>
          <a href="#result">Preview</a>
        </nav>
      </div>
    </header>
  );
}

export default Header;