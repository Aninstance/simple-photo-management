import './css/data-table.css';
import React from 'react';
import ModalImage from 'react-modal-image';
import DataTableAddTags from './data-table-add-tags';

const DataTableData = (props) => {

    const { record = {}, handleAddTags } = props

    return record.data.results.map((item, index) => {
        let { file_format, file_name, tags, public_img_tn_url } = item;
        let rowClasses = ['d-flex', 'dataTableRows'];
        let imgClasses = ['img-fluid', 'img-thumbnail', 'd-block', 'mx-auto'];
        let small_img_url = `${process.env.REACT_APP_ROUTE}${public_img_tn_url}/${file_name}-150_150${file_format}`;
        let medium_img_url = `${process.env.REACT_APP_ROUTE}${public_img_tn_url}/${file_name}-720_720${file_format}`;
        let full_img_url = `${process.env.REACT_APP_ROUTE}${public_img_tn_url}/${file_name}-1080_1080${file_format}`;
        return (<tr key={item.id} data-toggle="modal" className={rowClasses.join(' ')}>
            {/*<th scope="row">{item.id}</th>*/}
            <td className={'col-4 photo'}>
                <ModalImage
                    small={small_img_url}
                    medium={medium_img_url}
                    large={full_img_url}
                    alt={tags.join(', ')}
                    className={imgClasses.join(' ')}
                />
            </td>
            <td className={'col-4 tags'}>
                <ul>
                    {tags.map((tag, key) => <li key={key}>{tag}</li>)}
                </ul>
            </td>
            <td className={'action-col col-4 text-center'}>
                <DataTableAddTags handleAddTags={handleAddTags} recordItem={item} />
            </td>
        </tr>)
    });
};
export default DataTableData;

/*
Note 1: Be sure to pass values (e.g. {...item}) rather than obj (e.g. {item}),
otherwise the item obj (corresponding to the data results on the main table) will be updated with
values input in the console, as data.updateData would essentially
point to data.results, rather than being a separate, discrete object.
 */