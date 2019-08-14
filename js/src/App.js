import './App.css';

import React, { Component } from 'react';
import Emulator from './components/emulator/emulator.js'
import LogcatView from './components/emulator/views/logcat_view';


const environment = process.env.NODE_ENV || 'development'
var URI = window.location.protocol + '//' + window.location.hostname + ':' +
    window.location.port
if (environment === 'development') {
    URI = 'http://' + window.location.hostname + ':8080'
}

export default class App extends Component {
    state = {
        view: 'webrtc'
    }

    render() {
        const { view } = this.state
        return (
            <div className='container'>
                <p>Using emulator view: {view}</p>
                <button onClick={() => this.setState({view: 'fallback'})}>Fallback</button>
                <button onClick={() => this.setState({view: 'webrtc'})}>Webrtc</button>
                <button onClick={() => this.setState({view: 'png'})}>Png</button>
                <div className='leftpanel'><Emulator uri={URI} view={view} /></div>
                <div className='rightpanel'><LogcatView uri={URI} maxHistory='15' /></div>
            </div>
        )
    }
}
