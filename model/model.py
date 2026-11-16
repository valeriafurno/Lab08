from multiprocessing.managers import convert_to_error

from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        # TODO
        prezzi_media=[]
        for distributore in self._distributori:
            prezzi= distributore.get_prezzi() #tutti i prezzi
            prezzi_mese = [] # lista che mi contiene i prezzi del mese selezionato
            for prezzo in prezzi:
                if prezzo.data.month == mese:
                    prezzi_mese.append(prezzo.prezzo_litro) #aggiungo il prezzo litro di quel mese

            if len(prezzi_mese) > 0: #controllo che abbia almeno un elemento
                media = sum(prezzi_mese) / len(prezzi_mese)
                prezzi_media.append((distributore.nome, round(media, 3))) #salvo nella lista il nome del distributore e la sua media

        return prezzi_media


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # TODO
        if giorno == 8: #CONDIZIONE TERMINALE: sequenza 7 giorni completa
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo: # controllo se è la prima soluzione trovata
                    #oppure se il costo attuale è inferiore al costo minimo trovato precedentemente

                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        else:
            for distributore in prezzi_settimana:
                    prezzo = prezzi_settimana[distributore][giorno-1]
                    costo = prezzo * 100
                    if ultimo_distributore is not None and distributore != ultimo_distributore: #
                        costo += 5 #aggiungere 5 al costo quando non è il primo giorno e cambio distributore
                    sequenza_parziale.append(distributore)

                    self.__ricorsione(sequenza_parziale, giorno+1, distributore, costo_corrente+costo, prezzi_settimana)
                    sequenza_parziale.pop()  #backtracking: togliere ultima scelta per poter provare un altro distributore nello stesso giorno

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        # TODO
        prezzi_settimana = {}
        for distributore in self._distributori:
            prezzi= distributore.get_prezzi() #ottengo TUTTI i prezzi del distributore
            prezzi_filtrati=[] #prezzi dei primi 7 giorni
            for prezzo in prezzi:
                if prezzo.data.month == mese and prezzo.data.day<=7:
                    prezzi_filtrati.append(prezzo.prezzo_litro)
            prezzi_settimana[distributore.id] = prezzi_filtrati # associo al distributore la lista di prezzi filtrati
        return prezzi_settimana