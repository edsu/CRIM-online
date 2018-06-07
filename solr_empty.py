import solr
import sys
if __name__ == '__main__':
    print('Emptying Solr')
    solrconn = solr.SolrConnection('http://localhost:8080/crim-solr')
    solrconn.delete_query('*:*')
    solrconn.commit()
    sys.exit()
