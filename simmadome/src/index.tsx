import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import discordlogo from "./img/discord.png";
import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <React.StrictMode>
  	<Header />
    <App filter={null} gameId={null}/>
  </React.StrictMode>,
  document.getElementById('root')
);


function Header() {
  return (
    <div id="header">
        <div id="link_div">
            <a href="https://www.patreon.com/sixteen" className="link" target="_blank" rel="noopener noreferrer">Patreon</a><br />
            <a href="https://github.com/Sakimori/matteo-the-prestige" className="link" target="_blank" rel="noopener noreferrer">Github</a><br />
            <a href="https://twitter.com/intent/follow?screen_name=SIBR_XVI" className="link" target="_blank" rel="noopener noreferrer">Twitter</a>
        </div>
        <a href="/" className="page_header"><h2 className="page_header" style={{fontSize:"50px"} as React.CSSProperties}>THE SIMMADOME</h2></a>
        <h2 className="page_header">Join SIBR on <a href="https://discord.gg/UhAajY2NCW" className="link"><img src={discordlogo} alt="" height="30"/></a> to start your own games!</h2>
    </div>
  );
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
