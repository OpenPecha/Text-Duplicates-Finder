
def search(query, port):
	from py4j.java_gateway import JavaGateway, GatewayParameters
	from py4j.java_gateway import java_import
	
	gateway = JavaGateway(gateway_parameters=GatewayParameters(port=port))
	java_import(gateway.jvm, "net.sourceforge.docfetcher.gui.Application")
	application = gateway.jvm.net.sourceforge.docfetcher.gui.Application
	
	indexRegistry = application.getIndexRegistry()
	searcher = indexRegistry.getSearcher()
	results = searcher.search(query)
	return results

""" def main(query):
	dirs = []
	try:
		result_docs = search(query, 28834)
		for doc in result_docs:
			dirs.append(doc.getPathStr())
	except:
		print("ERROR: ")

    return dirs """

def main(query):
	dirs = []
	try:
		docs =search(query, 28834)
		for doc in docs:
			dirs.append(doc.getFilename())
	except:
		print("ERROR: ")
		
	return dirs			


if __name__ == "__main__":
	main("བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།")
