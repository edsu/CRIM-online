import json
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crim.settings')
import django

from importing.analysis_constants import *

django.setup()

FILE_IN = 'source/citations.json'
FILE_OUT = '../crim/fixtures/analysis.json'
NUMBERED_OUT = 'source/citations_numbered.json'
UNPROCESSED_OUT = 'source/not_imported.json'
LOG = 'source/analysis_import_log.txt'
OBSERVATION_COUNT = 0
RELATIONSHIP_COUNT = 0

# TODO: add "needs review" if has a same created_date as another one.
# TODO: add orphaned observations, but tag them as "needs review".
# TODO: note the duplicate observation at 2017-07-18T22:29:39; collapse this.


def process_json():
    '''Given an input file, write imported json to `new_fixture`, and
    put any unimported json in `unprocessed_json`.
    '''
    processed_data = []
    unprocessed_data = []
    log = []
    with open(FILE_IN, encoding='utf-8', newline='') as old_json_file:
        old_data = json.load(old_json_file)
    for item in old_data:
        handle_item(item, processed_data, unprocessed_data, log)
    with open(NUMBERED_OUT, 'w', encoding='utf-8') as numbered_file:
        # `old_data` has been updated with <R0> numbers
        numbered_file.write(json.dumps(old_data, indent=2))
    with open(FILE_OUT, 'w', encoding='utf-8') as new_fixture:
        new_fixture.write(json.dumps(processed_data))
    with open(UNPROCESSED_OUT, 'w', encoding='utf-8') as unprocessed_json_file:
        unprocessed_json_file.write(json.dumps(unprocessed_data, indent=2))
    with open(LOG, 'w', encoding='utf-8') as log_file:
        log_file.write('\n'.join(log))


def handle_item(item, processed_data, unprocessed_data, log):
    if eval(item['user']) not in USERS_TO_KEEP:
        pass  # leave_unprocessed(item, unprocessed_data, log, 'User {0} not in list of approved analysts.'.format(item['user']))
    elif len(item['scores']) > 2:
        leave_unprocessed(item, unprocessed_data, log, 'Too many scores (%d)' % len(item['scores']))
    elif 'relationships' not in item or not item['relationships']:
        leave_unprocessed(item, unprocessed_data, log, 'No relationships in item.')
    else:
        create_item(item, processed_data, unprocessed_data, log)


def leave_unprocessed(item, unprocessed_data, log, fault):
    item['fault'] = fault
    unprocessed_data.append(item)
    log.append('Item with timestamp {0} unproccesed: {1}'.format(item['created_at'], fault))


def create_item(item, processed_data, unprocessed_data, log):
    global RELATIONSHIP_COUNT
    possible_relationships = []
    for relationship in item['relationships']:
        if not relationship['type']:
            log.append('Relationship with timestamp {} unprocessed: null type'.format(item['created_at']))
        elif 'scoreA_ema' not in relationship or 'scoreB_ema' not in relationship:
            log.append('Relationship with timestamp {} unprocessed: EMA missing'.format(item['created_at']))
        else:
            possible_relationships.append(relationship)
    if not possible_relationships:
        leave_unprocessed(item, unprocessed_data, log, 'No relationships with EMA expressions')
        return
    elif len(possible_relationships) > 1:
        leave_unprocessed(item, unprocessed_data, log, 'Too many relationships ({})'.format(len(item['relationships'])))
        return
    else:
        relationship_to_process = possible_relationships[0]
        new_observations = create_observations(item, relationship_to_process, processed_data, unprocessed_data, log)
        new_relationship_fields = {}
        if new_observations:
            model_observation_fields, derivative_observation_fields = new_observations
            new_relationship_fields['observer'] = PEOPLE[item['user']]
            new_relationship_fields['model_observation'] = model_observation_fields['id']
            new_relationship_fields['derivative_observation'] = derivative_observation_fields['id']
            new_relationship_fields['model_piece'] = model_observation_fields['piece']
            new_relationship_fields['derivative_piece'] = derivative_observation_fields['piece']
            new_relationship_fields['created'] = item['created_at']
            new_relationship_fields['updated'] = item['created_at']
            new_relationship_fields['curated'] = False if 'needs_review' in item and item['needs_review'] else True
            model_observation_fields['curated'] = new_relationship_fields['curated']
            derivative_observation_fields['curated'] = new_relationship_fields['curated']
            add_relationship_types(relationship_to_process, new_relationship_fields)

            model_observation_row = {
                'model': 'crim.crimobservation',
                'fields': model_observation_fields,
                'pk': model_observation_fields['id'],
            }
            derivative_observation_row = {
                'model': 'crim.crimobservation',
                'fields': derivative_observation_fields,
                'pk': derivative_observation_fields['id'],
            }
            RELATIONSHIP_COUNT += 1
            relationship_to_process['relationship_id'] = '<R{}>'.format(RELATIONSHIP_COUNT)
            new_relationship_row = {
                'model': 'crim.crimrelationship',
                'fields': new_relationship_fields,
                'pk': RELATIONSHIP_COUNT,
            }
            processed_data.append(model_observation_row)
            processed_data.append(derivative_observation_row)
            processed_data.append(new_relationship_row)
        else:
            return


def create_observations(item, relationship, processed_data, unprocessed_data, log):
    global OBSERVATION_COUNT
    '''Create an observation for each observation in the old data.
    If there are more than two observations, don't process.
    '''
    model_observation = {}
    derivative_observation = {}
    if 'titleA' not in relationship or 'titleB' not in relationship:
        leave_unprocessed(item, unprocessed_data, log, 'Relationship does not contain titles.')
        return
    elif 'scoreA_ema' not in relationship or 'scoreB_ema' not in relationship:
        leave_unprocessed(item, unprocessed_data, log, 'Relationship does not contain EMA expressions.')
        return

    # Make a special exception for CRIM_Model_0022, which is a model-to-model relationship
    if 'CRIM_Model' in PIECES[relationship['titleA']] and 'CRIM_Model_0022' not in PIECES[relationship['titleB']]:
        model_observation['piece'] = PIECES[relationship['titleA']]
        derivative_observation['piece'] = PIECES[relationship['titleB']]
        model_observation['ema'] = relationship['scoreA_ema']
        derivative_observation['ema'] = relationship['scoreB_ema']
    else:
        model_observation['piece'] = PIECES[relationship['titleB']]
        derivative_observation['piece'] = PIECES[relationship['titleA']]
        model_observation['ema'] = relationship['scoreB_ema']
        derivative_observation['ema'] = relationship['scoreA_ema']

    model_observation['observer'] = PEOPLE[item['user']]
    derivative_observation['observer'] = PEOPLE[item['user']]
    model_observation['created'] = item['created_at']
    derivative_observation['created'] = item['created_at']
    model_observation['updated'] = item['created_at']
    derivative_observation['updated'] = item['created_at']

    # If looking up the observation in the item's observations
    # returns a result, use that data to add a type to the observation;
    # also copy the remarks. Otherwise, these fields simply aren't added.
    if 'observations' in item and item['observations']:
        for observation in item['observations']:
            if ('ema' in observation and observation['ema'] == model_observation['ema'] and
                    PIECES[observation['title']] == model_observation['piece']):
                add_musical_types(observation, model_observation)
            elif ('ema' in observation and observation['ema'] == derivative_observation['ema'] and
                  PIECES[observation['title']] == derivative_observation['piece']):
                add_musical_types(observation, derivative_observation)
            else:
                if 'title' not in observation:
                    log.append('Observation with timestamp {} unprocessed: without title and not associated with relationship.'.format(item['created_at']))
    # If the observation doesn't match the relationship (ie is an orphan),
    # mark as "needs review" and mention the situation in the remark.
                else:
                    add_orphan_observation(item, observation, processed_data)
                    log.append('Item with timestamp {} needs review: not associated with relationship'.format(item['created_at']))

    # Finally, return the new observations with unique ids.
    OBSERVATION_COUNT += 1
    model_observation['id'] = OBSERVATION_COUNT
    OBSERVATION_COUNT += 1
    derivative_observation['id'] = OBSERVATION_COUNT
    return (model_observation, derivative_observation)


def add_orphan_observation(item, observation, processed_data):
    global OBSERVATION_COUNT

    new_observation_fields = {}
    new_observation_fields['piece'] = PIECES[observation['title']]
    new_observation_fields['ema'] = observation['ema']

    new_observation_fields['observer'] = PEOPLE[item['user']]
    new_observation_fields['created'] = item['created_at']
    new_observation_fields['updated'] = item['created_at']
    new_observation_fields['curated'] = False

    OBSERVATION_COUNT += 1
    new_observation_row = {
        'model': 'crim.crimobservation',
        'pk': OBSERVATION_COUNT,
        'fields': new_observation_fields,
    }
    processed_data.append(new_observation_row)


def _add_list_as_string(item, base_name='voice'):
    combined_list = []
    count = 1
    while base_name + str(count) in item:
        combined_list.append(item[base_name + str(count)])
        count += 1
    return '\n'.join(combined_list)


def add_musical_types(observation, new_observation):
    '''Add the musical types and remarks of an observation to the
    new observation object.'''
    new_observation['remarks'] = observation['comment']
    if observation['type'] == 'mt-cf':
        new_observation['mt_cf'] = True
        new_observation['mt_cf_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_cf_dur'] = observation['dur']
        new_observation['mt_cf_mel'] = observation['mel']
    if observation['type'] == 'mt-sog':
        new_observation['mt_sog'] = True
        new_observation['mt_sog_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_sog_dur'] = observation['dur']
        new_observation['mt_sog_mel'] = observation['mel']
        new_observation['mt_sog_ostinato'] = observation['ost']
        new_observation['mt_sog_periodic'] = observation['per']
    if observation['type'] == 'mt-csog':
        new_observation['mt_csog'] = True
        new_observation['mt_csog_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_csog_dur'] = observation['dur']
        new_observation['mt_csog_mel'] = observation['mel']
    if observation['type'] == 'mt-cd':
        new_observation['mt_cd'] = True
        new_observation['mt_cd_voices'] = _add_list_as_string(observation['options'])
    if observation['type'] == 'mt-fg':
        new_observation['mt_fg'] = True
        new_observation['mt_fg_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_fg_int'] = observation['int']
        new_observation['mt_fg_tint'] = observation['tint']
        new_observation['mt_fg_periodic'] = observation['pe']
        new_observation['mt_fg_strict'] = observation['ste']
        new_observation['mt_fg_flexed'] = observation['fe']
        new_observation['mt_fg_sequential'] = observation['se']
        new_observation['mt_fg_inverted'] = observation['ie']
        new_observation['mt_fg_retrograde'] = observation['re']
    if observation['type'] == 'mt-pe':
        new_observation['mt_pe'] = True
        new_observation['mt_pe_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_pe_int'] = observation['int']
        new_observation['mt_pe_tint'] = observation['tint']
        new_observation['mt_pe_strict'] = observation['ste']
        new_observation['mt_pe_flexed'] = observation['fe']
        new_observation['mt_pe_flt'] = observation['fte']
        new_observation['mt_pe_sequential'] = observation['se']
        new_observation['mt_pe_added'] = observation['ae']
        new_observation['mt_pe_invertible'] = observation['ic']
    if observation['type'] == 'mt-id':
        new_observation['mt_id'] = True
        new_observation['mt_id_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_id_int'] = observation['int']
        new_observation['mt_id_tint'] = observation['tint']
        new_observation['mt_id_strict'] = observation['ste']
        new_observation['mt_id_flexed'] = observation['fe']
        new_observation['mt_id_flt'] = observation['fte']
        new_observation['mt_id_invertible'] = observation['ic']
    if observation['type'] == 'mt-nid':
        new_observation['mt_nid'] = True
        new_observation['mt_nid_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_nid_int'] = observation['int']
        new_observation['mt_nid_tint'] = observation['tint']
        new_observation['mt_nid_strict'] = observation['ste']
        new_observation['mt_nid_flexed'] = observation['fe']
        new_observation['mt_nid_flt'] = observation['fte']
        new_observation['mt_nid_sequential'] = observation['se']
        new_observation['mt_nid_invertible'] = observation['ic']
    if observation['type'] == 'mt-hr':
        new_observation['mt_hr'] = True
        new_observation['mt_hr_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_hr_simple'] = observation['s']
        new_observation['mt_hr_staggered'] = observation['st']
        new_observation['mt_hr_sequential'] = observation['se']
        new_observation['mt_hr_fauxbourdon'] = observation['fa']
    if observation['type'] == 'mt-cad':
        new_observation['mt_cad'] = True
        new_observation['mt_cad_cantizans'] = observation['options']['voice1']
        new_observation['mt_cad_tenorizans'] = observation['options']['voice2']
        if observation['a']:
            assert not observation['ph'] and not observation['p']
            new_observation['mt_cad_type'] = 'authentic'
        elif observation['ph']:
            assert not observation['a'] and not observation['p']
            new_observation['mt_cad_type'] = 'phrygian'
        elif observation['p']:
            assert not observation['a'] and not observation['ph']
            new_observation['mt_cad_type'] = 'plagal'
        new_observation['mt_cad_tone'] = observation['tone']
        new_observation['mt_cad_dtv'] = observation['options']['dove_voice1']
        new_observation['mt_cad_dti'] = observation['dove']
    if observation['type'] == 'mt-int':
        new_observation['mt_int'] = True
        new_observation['mt_int_voices'] = _add_list_as_string(observation['options'])
        new_observation['mt_int_p6'] = observation['p6']
        new_observation['mt_int_p3'] = observation['p3']
        new_observation['mt_int_c35'] = observation['c35']
        new_observation['mt_int_c83'] = observation['c83']
        new_observation['mt_int_c65'] = observation['c65']
    if observation['type'] == 'mt-fp':
        new_observation['mt_fp'] = True
        new_observation['mt_fp_ir'] = observation['ir']
        new_observation['mt_fp_range'] = observation['r']
        new_observation['mt_fp_comment'] = observation['comment']


def add_relationship_types(old_relationship, new_relationship):
    '''Add the relationship types and remarks of an relationship to the
    new relationship object.'''
    new_relationship['remarks'] = old_relationship['comment']
    if old_relationship['type'] == 'rt-q':
        new_relationship['rt_q'] = True
        new_relationship['rt_q_x'] = old_relationship['ex']
        new_relationship['rt_q_monnayage'] = old_relationship['mo']
    if old_relationship['type'] == 'rt-tm':
        new_relationship['rt_tm'] = True
        new_relationship['rt_tm_snd'] = old_relationship['snd']
        new_relationship['rt_tm_minv'] = old_relationship['minv']
        new_relationship['rt_tm_retrograde'] = old_relationship['r']
        new_relationship['rt_tm_ms'] = old_relationship['ms']
        new_relationship['rt_tm_transposed'] = old_relationship['t']
        new_relationship['rt_tm_invertible'] = old_relationship['td']
    if old_relationship['type'] == 'rt-tnm':
        new_relationship['rt_tnm'] = True
        new_relationship['rt_tnm_embellished'] = old_relationship['em']
        new_relationship['rt_tnm_reduced'] = old_relationship['re']
        new_relationship['rt_tnm_amplified'] = old_relationship['am']
        new_relationship['rt_tnm_truncated'] = old_relationship['tr']
        new_relationship['rt_tnm_ncs'] = old_relationship['ncs']
        new_relationship['rt_tnm_ocs'] = old_relationship['ocs']
        new_relationship['rt_tnm_ocst'] = old_relationship['ocst'] if 'ocst' in old_relationship else False
        new_relationship['rt_tnm_nc'] = old_relationship['nc']
    if old_relationship['type'] == 'rt-nm':
        new_relationship['rt_nm'] = True
    if old_relationship['type'] == 'rt-om':
        new_relationship['rt_om'] = True


if __name__ == '__main__':
    process_json()
