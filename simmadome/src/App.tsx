import React from 'react';
import './App.css';

class App extends React.Component {
  render() {
    return (
      <div className="App">
        <Filters />
        <Grid />
        <Footer />
      </div>
    );
  }
}

class Filters extends React.Component {
  render() {
    return (
      <div id="filters">
          <div>Filter:</div>
          <button className="filter" id="selected_filter">All</button>
      </div>
    );
  }
}

function Grid() {
  return (
    <section className="container" id="container">
      <div className="emptyslot" />
    </section>
  );
}

function Footer() {
  return (
    <div id="footer">
        <div></div>
    </div>
  );
}

export default App;
