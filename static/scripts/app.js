import React from 'react'
import {Route,Router} from 'react-router'

import Lobby from './lobby'
import Main from './main'
import CommonComponent from "./common"

class App extends React.Component {
    render(){
        return(
            <div>
                <Router>
                    <Route path={"/lobby"} component={Lobby}/>
                    <Route path={"/main"} component={Main}/>
                </Router>
                <CommonComponent/>
            </div>
        )}
}

export default App