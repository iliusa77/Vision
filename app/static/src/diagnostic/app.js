import React from 'react';
import { Router, Route, IndexRoute, Link, hashHistory } from 'react-router'
import {Component} from 'react'
import { render } from 'react-dom'
import Equipment from './Components/Equipment';
import Home from './Components/Home';
import Campaign from './Components/Campaign';

import AddEquipmentForm from './AddEquipmentForm';
import ChooseTestForm from './ChooseTestForm';
import ElectricalProfileForm from './ElectricalProfileForm';
import FluidProfileForm from './FluidProfileForm';
import TestList from './TestList';

import NewTestForm from './NewTestForm'; 
import CreatedByForm from './CampaignForm_modules/CreatedByForm';
import NewMaterialForm from './NewTestForm_modules/NewMaterialForm';
import NewContractForm from './CampaignForm_modules/NewContractForm';
import NewLabForm from './CampaignForm_modules/NewLabForm';
import NewFluidForm from './NewTestForm_modules/NewFluidForm';
import NewRecommendationForm from './NewTestForm_modules/NewRecommendationForm';


const App = React.createClass({
  render() {
    return (

        <div className="content">
            <div>
                <ul>
                    <li><Link to='/home'>Home</Link></li>
                    <li><Link to='/campaign'>New Campaign</Link></li>
                    <li><Link to='/equipment'>Equipment</Link></li>
                    <li><Link to='/add_equipment'>Add Equipment</Link></li>
                    <li><Link to='/testlist'>Testlist</Link></li>
                    <li><Link to='/add_test'>New Test</Link></li>
                    <li><Link to='/electro'>Electrical Profile</Link></li>
                    <li><Link to='/fluid'>Fluid Profile</Link></li>
                    <li><Link to='/choose_profile'>Choose Test Profile</Link></li>
                    <li><Link to='/add_createdby'>created by</Link></li>
                    <li><Link to='/add_contract'>contract</Link></li>
                    <li><Link to='/add_lab'>lab</Link></li>
                    <li><Link to='/add_material'>material</Link></li>
                    <li><Link to='/add_fluid'>new fluid</Link></li>
                    <li><Link to='/add_recommend'>recommend</Link></li>
                </ul>
                <Link to='/campaign' className="btn btn-success btn-large">Start New Campaign</Link>

            </div>
            <div className='app-container'>
                <hr/>
                {this.props.children}
            </div>
        </div>
    )
  }
});

render((
    <Router history={hashHistory}>
        <Route path="/" component={App}>
            <IndexRoute component={Home} />
            <Route path="campaign" component={Campaign} />
            <Route path="equipment" component={Equipment} />
            <Route path="add_equipment/:campaign" component={AddEquipmentForm} />
            <Route path="testlist/:campaign" component={TestList} />
            <Route path="electro" component={ElectricalProfileForm} />
            <Route path="fluid" component={FluidProfileForm} />
            <Route path="choose_profile" component={ChooseTestForm} />
            <Route path="add_test" component={NewTestForm} />
            <Route path="add_createdby" component={CreatedByForm} />
            <Route path="add_contract" component={NewContractForm} />
            <Route path="add_lab" component={NewLabForm} />
            <Route path="add_material" component={NewMaterialForm} />
            <Route path="add_fluid" component={NewFluidForm} />
            <Route path="add_recommend" component={NewRecommendationForm} />
        </Route>
    </Router>
), document.getElementById('app'));

